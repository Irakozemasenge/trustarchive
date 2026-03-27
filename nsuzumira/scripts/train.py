"""
Fine-tuning de Gemma-7b avec QLoRA pour créer Nsuzumira
Modèle spécialisé analyse documents officiels burundais

Usage:
    python scripts/train.py
    python scripts/train.py --base_model google/gemma-7b --epochs 3
"""
import os
import argparse
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune Gemma-7b -> Nsuzumira")
    parser.add_argument("--base_model", default="google/gemma-7b")
    parser.add_argument("--data_dir", default="../data")
    parser.add_argument("--output_dir", default="../model/nsuzumira-lora")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max_seq_length", type=int, default=1024)
    parser.add_argument("--hf_token", default=os.environ.get("HF_TOKEN", ""))
    parser.add_argument("--push_to_hub", action="store_true")
    parser.add_argument("--hub_model_id", default="Irakozemasenge/nsuzumira")
    return parser.parse_args()


def load_model_and_tokenizer(model_name, hf_token):
    print(f"Chargement du modele de base: {model_name}")

    # Configuration 4-bit quantization (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        token=hf_token,
        add_eos_token=True,
        padding_side="right",
    )
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        token=hf_token,
        torch_dtype=torch.bfloat16,
    )

    model = prepare_model_for_kbit_training(model)
    return model, tokenizer


def apply_lora(model):
    """Applique les adaptateurs LoRA sur Gemma-7b"""
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,                          # Rang LoRA
        lora_alpha=32,                 # Scaling
        lora_dropout=0.05,
        bias="none",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def main():
    args = parse_args()

    # Générer le dataset si pas encore fait
    train_path = os.path.join(args.data_dir, "train.jsonl")
    eval_path = os.path.join(args.data_dir, "eval.jsonl")

    if not os.path.exists(train_path):
        print("Generation du dataset...")
        os.chdir(args.data_dir)
        os.system("python generate_dataset.py")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Charger le dataset
    print("Chargement du dataset...")
    dataset = load_dataset(
        "json",
        data_files={"train": train_path, "eval": eval_path}
    )
    print(f"Train: {len(dataset['train'])} exemples | Eval: {len(dataset['eval'])} exemples")

    # Charger modèle + tokenizer
    model, tokenizer = load_model_and_tokenizer(args.base_model, args.hf_token)

    # Appliquer LoRA
    model = apply_lora(model)

    # Configuration d'entraînement
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        fp16=False,
        bf16=True,
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        report_to="none",
        push_to_hub=args.push_to_hub,
        hub_model_id=args.hub_model_id if args.push_to_hub else None,
        hub_token=args.hf_token if args.push_to_hub else None,
    )

    # Trainer SFT (Supervised Fine-Tuning)
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["eval"],
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        args=training_args,
        packing=False,
    )

    print("\n=== Debut du fine-tuning Nsuzumira ===")
    print(f"Modele de base : {args.base_model}")
    print(f"Epochs         : {args.epochs}")
    print(f"Batch size     : {args.batch_size}")
    print(f"Learning rate  : {args.lr}")
    print(f"Output         : {args.output_dir}")
    print("=" * 40)

    trainer.train()

    # Sauvegarder les poids LoRA
    print(f"\nSauvegarde des poids LoRA dans {args.output_dir}")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    # Sauvegarder la config du modèle
    model_card = f"""---
language:
- fr
- rn
- en
license: gemma
base_model: google/gemma-7b
tags:
- nsuzumira
- trustarchive
- document-analysis
- burundi
- lora
- qlora
---

# Nsuzumira

**Nsuzumira** (Kirundi: "Vérifier/Authentifier") est un modèle de langage
fine-tuné sur Gemma-7b, spécialisé dans l'analyse de documents officiels burundais.

Développé dans le cadre de **TrustArchive.bi** — Formation des formateurs BuruDigi.

## Capacités
- Analyse et résumé de documents officiels
- Extraction d'informations clés (bénéficiaire, dates, numéros)
- Support: Diplômes, Actes notariés, Attestations, Casiers judiciaires
- Langues: Français, Kirundi, Anglais

## Usage
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("google/gemma-7b")
model = PeftModel.from_pretrained(base, "Irakozemasenge/nsuzumira")
tokenizer = AutoTokenizer.from_pretrained("Irakozemasenge/nsuzumira")
```
"""
    with open(os.path.join(args.output_dir, "README.md"), "w") as f:
        f.write(model_card)

    if args.push_to_hub:
        print(f"\nPublication sur HuggingFace Hub: {args.hub_model_id}")
        trainer.push_to_hub()

    print("\n=== Fine-tuning Nsuzumira termine avec succes ===")


if __name__ == "__main__":
    main()

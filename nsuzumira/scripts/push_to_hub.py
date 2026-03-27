"""
Publie Nsuzumira sur HuggingFace Hub
Usage: python scripts/push_to_hub.py --token hf_xxx
"""
import os
import argparse
from huggingface_hub import HfApi, create_repo


def push(model_path, hub_id, token):
    api = HfApi()

    print(f"Creation du repo: {hub_id}")
    try:
        create_repo(hub_id, token=token, private=False, exist_ok=True)
    except Exception as e:
        print(f"Repo existe deja ou erreur: {e}")

    print(f"Upload des fichiers depuis {model_path}...")
    api.upload_folder(
        folder_path=model_path,
        repo_id=hub_id,
        token=token,
        commit_message="feat: Nsuzumira v1.0 - Fine-tuned Gemma-7b pour documents burundais",
    )
    print(f"Nsuzumira publie sur: https://huggingface.co/{hub_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="../model/nsuzumira-lora")
    parser.add_argument("--hub_id", default="Irakozemasenge/nsuzumira")
    parser.add_argument("--token", default=os.environ.get("HF_TOKEN", ""))
    args = parser.parse_args()

    if not args.token:
        print("Fournissez --token ou definissez HF_TOKEN")
        exit(1)

    push(args.model_path, args.hub_id, args.token)

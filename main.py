"""Run the multi-agent book writer:  python main.py"""
import argparse

from dotenv import load_dotenv

from bookwriter.llm import LLM
from bookwriter.pipeline import BookPipeline


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="Multi-agent book writer")
    ap.add_argument("--provider", choices=["gemini", "groq", "openrouter", "ollama", "anthropic", "openai"], help="LLM provider (default: auto-detect from the key in .env)")
    ap.add_argument("--model", help="Model name (default depends on provider)")
    ap.add_argument("--rounds", type=int, default=3, help="Max revision rounds per chapter (default 3)")
    ap.add_argument("--out", default="output", help="Output folder (default: output)")
    args = ap.parse_args()

    llm = LLM(args.provider, args.model)
    print(f"Using {llm.provider} / {llm.model}\n")
    BookPipeline(llm, out_dir=args.out, max_rounds=args.rounds).run()


if __name__ == "__main__":
    main()

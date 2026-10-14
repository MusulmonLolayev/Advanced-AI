"""Run τ²-bench's CLI with every hidden default model switched to DeepSeek.

τ²-bench v1.0.1 judges natural-language assertions with gpt-4.1 and has no CLI flag for it, so without an OpenAI key
those tasks end in an infrastructure error. Here the judge (and the environment interface) use the same DeepSeek
model as the agent. Scores are therefore not comparable with the public leaderboard, which uses gpt-4.1 as judge.
    cd tau2-bench && uv run python ../run_tau2.py run --domain retail ...
"""
import sys

import tau2.config as config
import tau2.environment.utils.interface_agent as interface_agent
import tau2.evaluator.evaluator_nl_assertions as nl

JUDGE = "deepseek/deepseek-v4-flash"
config.DEFAULT_LLM_NL_ASSERTIONS = nl.DEFAULT_LLM_NL_ASSERTIONS = JUDGE
config.DEFAULT_LLM_ENV_INTERFACE = interface_agent.DEFAULT_LLM_ENV_INTERFACE = JUDGE

from tau2.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.argv[0] = "tau2"
    sys.exit(main())

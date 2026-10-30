import argparse

from prompt_loader import PromptLoader
from agent_runner import AgentRunner
from file_manager import FileManager


# =========================
# PROJECT FILES
# =========================

REQUEST_FILE = (
    "../projects/crm-system/business/request.md"
)

BUSINESS_ANALYSIS_FILE = (
    "../projects/crm-system/business/business-analysis.md"
)

PRD_FILE = (
    "../projects/crm-system/business/prd.md"
)

UIUX_FILE = (
    "../projects/crm-system/design/uiux-design.md"
)

ARCHITECTURE_FILE = (
    "../projects/crm-system/architecture/technical-design.md"
)

API_CONTRACT_FILE = (
    "../projects/crm-system/api/api-contract.md"
)

JIRA_FILE = (
    "../projects/crm-system/jira/jira-plan.md"
)

STORY_OUTPUT_DIR = (
    "../projects/crm-system/jira/stories"
)

STORY_INDEX_FILE = (
    "../projects/crm-system/jira/story-artifacts.md"
)

BACKEND_OUTPUT_DIR = (
    "../projects/crm-system/backend"
)

BACKEND_FILE = (
    "../projects/crm-system/backend/backend-implementation.md"
)


# =========================
# HELPERS
# =========================

def get_story_file(story_id: str) -> str:
    return (
        f"{STORY_OUTPUT_DIR}/{story_id}.md"
    )

def get_backend_file(
    story_id: str
) -> str:

    return (
        f"{BACKEND_OUTPUT_DIR}/{story_id}-backend.md"
    )

# =========================
# SHARED RUNNER
# =========================

runner = AgentRunner()


def execute(
    agent_name: str,
    prompt_file: str,
    input_files: list[str],
    output_file: str,
):

    print(f"\n[INFO] Running {agent_name}")

    prompt = PromptLoader.build_prompt(
        prompt_file=prompt_file,
        input_files=input_files,
    )

    result = runner.run(
        agent_name=agent_name,
        prompt=prompt,
    )

    FileManager.write(
        output_file,
        result,
    )

    print(
        f"[SUCCESS] Generated: {output_file}"
    )


# =========================
# V0
# Business Analysis
# =========================

def generate_business_analysis():

    execute(
        agent_name="business_enablement",
        prompt_file="../prompts/create-business-analysis.md",
        input_files=[
            REQUEST_FILE
        ],
        output_file=BUSINESS_ANALYSIS_FILE,
    )


# =========================
# V1
# PRD
# =========================

def generate_prd():

    execute(
        agent_name="po",
        prompt_file="../prompts/create-prd.md",
        input_files=[
            BUSINESS_ANALYSIS_FILE
        ],
        output_file=PRD_FILE,
    )


# =========================
# V2
# UIUX
# =========================

def generate_uiux():

    execute(
        agent_name="uiux",
        prompt_file="../prompts/create-uiux-design.md",
        input_files=[
            PRD_FILE
        ],
        output_file=UIUX_FILE,
    )


# =========================
# V3
# Architecture
# =========================

def generate_architecture():

    execute(
        agent_name="architect",
        prompt_file="../prompts/create-architecture.md",
        input_files=[
            BUSINESS_ANALYSIS_FILE,
            PRD_FILE,
            UIUX_FILE,
        ],
        output_file=ARCHITECTURE_FILE,
    )


# =========================
# V4
# API Contract
# =========================

def generate_api_contract():

    execute(
        agent_name="api_contract",
        prompt_file="../prompts/create-api-contract.md",
        input_files=[
            BUSINESS_ANALYSIS_FILE,
            PRD_FILE,
            UIUX_FILE,
            ARCHITECTURE_FILE,
        ],
        output_file=API_CONTRACT_FILE,
    )


# =========================
# V5
# Jira
# =========================

def generate_jira():

    execute(
        agent_name="jira",
        prompt_file="../prompts/create-jira-task.md",
        input_files=[
            BUSINESS_ANALYSIS_FILE,
            PRD_FILE,
            UIUX_FILE,
            ARCHITECTURE_FILE,
            API_CONTRACT_FILE,
        ],
        output_file=JIRA_FILE,
    )


# =========================
# V6
# Story Artifact Index
# =========================

def generate_story_artifacts():

    execute(
        agent_name="story_generator",
        prompt_file="../prompts/create-story-artifacts.md",
        input_files=[
            JIRA_FILE,
        ],
        output_file=STORY_INDEX_FILE,
    )


# =========================
# V6.1
# Story Detail
# =========================

def generate_story_detail(
    story_id: str
):

    execute(
        agent_name="story_detail_generator",
        prompt_file="../prompts/create-story-details.md",
        input_files=[
            STORY_INDEX_FILE,
            JIRA_FILE,
            BUSINESS_ANALYSIS_FILE,
            PRD_FILE,
            UIUX_FILE,
            ARCHITECTURE_FILE,
            API_CONTRACT_FILE,
        ],
        output_file=get_story_file(story_id),
    )


# =========================
# V7
# Backend
# =========================

def generate_backend(
    story_id: str
):

    execute(
        agent_name="backend",
        prompt_file="../prompts/generate-backend.md",
        input_files=[
            get_story_file(story_id),
            ARCHITECTURE_FILE,
            API_CONTRACT_FILE,
        ],
        output_file=get_backend_file(
            story_id
        ),
    )


# =========================
# FULL PLANNING WORKFLOW
# =========================

def full_workflow():

    generate_business_analysis()

    generate_prd()

    generate_uiux()

    generate_architecture()

    generate_api_contract()

    generate_jira()

    generate_story_artifacts()

    print(
        "\n[SUCCESS] Planning Complete"
    )

    print(
        "\n[NEXT] Generate Story Detail"
    )

    print(
        "python main.py "
        "--step story-detail "
        "--story CRM-STORY-001"
    )

    print(
        "\n[NEXT] Generate Backend"
    )

    print(
        "python main.py "
        "--step backend "
        "--story CRM-STORY-001"
    )


# =========================
# CLI
# =========================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--step",
        required=True,
        choices=[
            "business-analysis",
            "prd",
            "uiux",
            "architecture",
            "api-contract",
            "jira",
            "story-artifacts",
            "story-detail",
            "backend",
            "full",
        ]
    )

    parser.add_argument(
        "--story",
        required=False,
        help="Story ID, e.g. CRM-STORY-001"
    )

    args = parser.parse_args()

    if (
        args.step in [
            "story-detail",
            "backend",
        ]
        and not args.story
    ):
        parser.error(
            "--story is required for story-detail and backend"
        )

    if args.step == "business-analysis":

        generate_business_analysis()

    elif args.step == "prd":

        generate_prd()

    elif args.step == "uiux":

        generate_uiux()

    elif args.step == "architecture":

        generate_architecture()

    elif args.step == "api-contract":

        generate_api_contract()

    elif args.step == "jira":

        generate_jira()

    elif args.step == "story-artifacts":

        generate_story_artifacts()

    elif args.step == "story-detail":

        generate_story_detail(
            args.story
        )

    elif args.step == "backend":

        generate_backend(
            args.story
        )

    elif args.step == "full":

        full_workflow()


if __name__ == "__main__":
    main()
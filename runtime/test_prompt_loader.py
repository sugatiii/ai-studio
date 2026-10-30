from prompt_loader import PromptLoader


prompt = PromptLoader.build_prompt(
    prompt_file="../prompts/create-prd.md",
    input_files=["../projects/crm-system/business/request.md"],
)

print(prompt)
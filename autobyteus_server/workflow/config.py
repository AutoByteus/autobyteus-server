"""
The WORKFLOW_CONFIG dictionary defines the structure of the workflow, including steps and substeps.
Each step is defined as a key-value pair, where the key is the step name and the value is a dictionary containing:
    - 'step_class': The class representing the step.
    - 'steps': A dictionary of substeps, if any, following the same structure.
For example, the 'requirement_step' has a 'refine' substep with its own class.
"""
from autobyteus_server.workflow.steps.architecture_design.architecture_design_step import ArchitectureDesignStep
from autobyteus_server.workflow.steps.requirement.requirement_step import RequirementStep
from autobyteus_server.workflow.steps.requirement_refine.requirement_refine_step import RequirementRefineStep
from autobyteus_server.workflow.steps.run_tests_step.run_tests_step import RunTestsStep
from autobyteus_server.workflow.steps.subtask_implementation.subtask_implementation_step import SubtaskImplementationStep
from autobyteus_server.workflow.steps.tests_generation.tests_generation_step import TestsGenerationStep
from autobyteus_server.workflow.steps.ux_design.ux_design_step import UXDesignStep
from autobyteus_server.workflow.steps.article_writing.article_writing_step import ArticleWritingStep
from autobyteus_server.workflow.steps.question_answering.question_answering_step import QuestionAnsweringStep
from autobyteus_server.workflow.steps.prompt_creation.prompt_creation_step import PromptCreationStep
from autobyteus_server.workflow.steps.prompt_refine.prompt_refine_step import PromptRefineStep
from autobyteus_server.workflow.steps.documentation.documentation_step import DocumentationStep
from autobyteus_server.workflow.types.workflow_template_config import WorkflowTemplateStepsConfig

WORKFLOW_CONFIG: WorkflowTemplateStepsConfig = {
    'steps': {
        'requirement_step': {
            'step_class': RequirementStep,
            'steps': {
                'refine': {
                    'step_class': RequirementRefineStep
                }
            },
        },
        'architecture_design': {
            'step_class': ArchitectureDesignStep
        },
        'ux_design': {
            'step_class': UXDesignStep
        },
        'test_generation_step': {
            'step_class': TestsGenerationStep,
        },
        'implementation_step': {
            'step_class': SubtaskImplementationStep,
        },
        'testing_step': {
            'step_class': RunTestsStep,
        },
        'article_writing': {
            'step_class': ArticleWritingStep,
        },
        'question_answering': {
            'step_class': QuestionAnsweringStep,
        },
        'prompt_creation': {
            'step_class': PromptCreationStep,
        },
        'prompt_refine': {
            'step_class': PromptRefineStep,
        },
        'documentation': {
            'step_class': DocumentationStep,
        },
    }
}
##
## Integration tests for the agent.py module
##
## These tests use 'pytest-mock' to "mock" the
## slow-loading 'transformers.pipeline' function. This allows us to
## test our agent's internal logic without downloading or
## running the actual multi-GB NLP models.
##

import pytest
from unittest.mock import MagicMock, patch
from src.agent import IntelligentFormAgent
import pandas as pd
import os

## Define what a fake QA and Summary pipeline should return
MOCK_QA_RESULT = {"answer": "Mocked Answer", "score": 0.99}
MOCK_SUMMARY_RESULT =

@pytest.fixture
def mocked_agent():
    ##
    ## This fixture creates an IntelligentFormAgent, but *intercepts*
    ## the 'pipeline' call from the 'transformers' library.
    ## 
    ## Instead of loading the real models, we substitute
    ## MagicMock objects.
    ##
    ## We patch 'src.agent.pipeline', which is where 'agent.py' imports it
    with patch('src.agent.pipeline') as mock_pipeline:
        ## Configure the mock to return different fakes based on the task
        mock_qa_pipe = MagicMock(return_value=MOCK_QA_RESULT)
        mock_summ_pipe = MagicMock(return_value=MOCK_SUMMARY_RESULT)
        
        def side_effect(task, model):
            if task == "question-answering":
                return mock_qa_pipe
            if task == "summarization":
                return mock_summ_pipe
            return MagicMock()
            
        mock_pipeline.side_effect = side_effect
        
        ## Now, when IntelligentFormAgent() is called,
        ## it will use our MagicMocks instead of the real pipelines
        agent = IntelligentFormAgent()
        
        ## We attach the mocks to the agent object so we can
        ## inspect them during the test
        agent.mock_qa_pipe = mock_qa_pipe
        agent.mock_summ_pipe = mock_summ_pipe
        agent.mock_pipeline_loader = mock_pipeline
        yield agent


def test_agent_init(mocked_agent):
    ## Tests that the agent initializes and calls pipeline() correctly.
    assert mocked_agent is not None
    
    ## Check that 'pipeline' was called twice (once for QA, once for summ)
    assert mocked_agent.mock_pipeline_loader.call_count == 2
    mocked_agent.mock_pipeline_loader.assert_any_call(
        "question-answering", model=pytest.ANY
    )
    mocked_agent.mock_pipeline_loader.assert_any_call(
        "summarization", model=pytest.ANY
    )


@patch('src.extraction.extract_text_from_pdf', return_value="Mocked PDF context")
def test_agent_qa(mock_extractor, mocked_agent):
    ##
    ## Tests the process_single_form_qa method.
    ## We mock *both* the extractor and the pipeline.
    ##
    question = "What is the total?"
    result = mocked_agent.process_single_form_qa("fake/path.pdf", question)
    
    ## 1. Assert our mock extractor was called
    mock_extractor.assert_called_with("fake/path.pdf")
    
    ## 2. Assert our mock QA pipeline was called with the right args
    mocked_agent.mock_qa_pipe.assert_called_with(
        question=question, 
        context="Mocked PDF context"
    )
    
    ## 3. Assert we got the expected mock result back
    assert result == MOCK_QA_RESULT


@patch('src.extraction.extract_text_from_pdf', return_value="Mocked PDF context")
def test_agent_summary(mock_extractor, mocked_agent):
    ## Tests the process_single_form_summary method.
    result = mocked_agent.process_single_form_summary("fake/path.pdf")
    
    ## 1. Assert our mock extractor was called
    mock_extractor.assert_called_with("fake/path.pdf")
    
    ## 2. Assert our mock summary pipeline was called
    mocked_agent.mock_summ_pipe.assert_called_with(
        "Mocked PDF context", 
        max_length=pytest.ANY, 
        min_length=pytest.ANY, 
        do_sample=False
    )
    
    ## 3. Assert we got the expected mock result back
    assert result == MOCK_SUMMARY_RESULT


@patch('src.agent.IntelligentFormAgent.process_single_form_qa', return_value=MOCK_QA_RESULT)
@patch('os.listdir', return_value=['a.pdf', 'b.pdf'])
def test_agent_holistic(mock_listdir, mock_single_qa, mocked_agent):
    ## Tests the holistic insights method.
    question = "What is the total?"
    df = mocked_agent.process_multiple_forms_holistic("fake/dir", question)
    
    ## 1. Assert it called listdir
    mock_listdir.assert_called_with("fake/dir")
    
    ## 2. Assert it called the QA function for each PDF found
    assert mock_single_qa.call_count == 2
    mock_single_qa.assert_any_call(os.path.join("fake/dir", "a.pdf"), question)
    
    ## 3. Assert the resulting DataFrame is correct
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["file", "question", "answer", "score"]
    assert df.iloc["answer"] == "Mocked Answer"
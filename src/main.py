##
## Main CLI Entry Point
##
## This script provides a command-line interface to run the
## IntelligentFormAgent. It uses argparse with sub-commands
## [11, 12, 13] to handle the different agent functionalities.
##
## Example Usage:
## $ python -m src.main qa --path "data/sample.pdf" --question "What is the total?"
## $ python -m src.main summarize --path "data/sample.pdf"
## $ python -m src.main holistic --dir "data/" --question "What is the total?"
##

import argparse
import logging
import sys

from src.agent import IntelligentFormAgent

## Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(args: argparse.Namespace):
    ##
    ## Main logic dispatcher.
    ## Initializes the agent and calls the correct method based on the sub-command.
    ##
    ## The agent is initialized here. This is where models are loaded.
    ## This can take a few seconds.
    try:
        agent = IntelligentFormAgent()
    except Exception as e:
        logging.error(f"Failed to initialize the agent. Aborting. Error: {e}")
        sys.exit(1)

    ## Dispatch to the correct function based on the 'command'
    if args.command == 'qa':
        result = agent.process_single_form_qa(args.path, args.question)
        print("\n--- QA Result ---")
        print(f"Question: {args.question}")
        print(f"Answer:   {result.get('answer', 'N/A')}")
        print(f"Score:    {result.get('score', 0.0):.4f}")

    elif args.command == 'summarize':
        result_list = agent.process_single_form_summary(args.path)
        print("\n--- Summary Result ---")
        ## FIX: The pipeline returns a list, so we get the first item
        if result_list and len(result_list) > 0:
            print(result_list.get('summary_text', 'N/A'))
        else:
            print("No summary could be generated.")

    elif args.command == 'holistic':
        df_results = agent.process_multiple_forms_holistic(args.dir, args.question)
        print(f"\n--- Holistic Analysis for Question: '{args.question}' ---")
        print(df_results.to_string())
        ## Optional: Save to CSV
        ## df_results.to_csv("holistic_results.csv", index=False)
        ## print("\nResults also saved to 'holistic_results.csv'")


if __name__ == "__main__":
    ## This pattern [12, 13] makes the script runnable
    parser = argparse.ArgumentParser(description="Intelligent Form Agent CLI.")
    
    ## We use sub-parsers [11, 12, 13] for a clean command structure
    subparsers = parser.add_subparsers(dest="command", required=True, help="The action to perform")

    ## --- QA Sub-parser ---
    qa_parser = subparsers.add_parser('qa', help="Ask a question about a single form")
    qa_parser.add_argument('--path', type=str, required=True, help="Path to the PDF form")
    qa_parser.add_argument('--question', type=str, required=True, help="The question to ask")

    ## --- Summarize Sub-parser ---
    summ_parser = subparsers.add_parser('summarize', help="Generate a summary of a single form")
    summ_parser.add_argument('--path', type=str, required=True, help="Path to the PDF form")

    ## --- Holistic Sub-parser ---
    holistic_parser = subparsers.add_parser('holistic', help="Ask a question across multiple forms")
    holistic_parser.add_argument('--dir', type=str, required=True, help="Directory containing PDF forms")
    holistic_parser.add_argument('--question', type=str, required=True, help="The *same* question to ask all forms")

    parsed_args = parser.parse_args()
    main(parsed_args)
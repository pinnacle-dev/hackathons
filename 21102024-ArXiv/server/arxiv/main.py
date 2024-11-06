import logging
import send_functions

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        filename="arxiv_paper_updates.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Starting ArXiv paper checker.")
    send_functions.check_for_new_papers()
    logging.info("ArXiv paper checker finished.")

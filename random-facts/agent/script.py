import logging
from send import daily_send_fun_facts

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        filename="fun_facts.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Sending fun facts...")
    daily_send_fun_facts()
    logging.info("Fun facts sent!")

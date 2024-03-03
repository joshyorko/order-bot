from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from pathlib import Path
import shutil
from time import sleep



pdf = PDF()


website = "https://robotsparebinindustries.com/#/robot-order"

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        screenshot="only-on-failure",
  
    )
    download_csv_file()
    open_robot_order_website()
    close_annoying_modal()
    orders = get_orders()
    fill_the_form(orders)
    archive_receipts()

    
    


def download_csv_file():
    """
    Downloads a CSV file from a given URL.

    This function uses the HTTP class to download a CSV file from the specified URL.
    The downloaded file will overwrite any existing file with the same name.

   
    """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)


def fill_the_form(orders):
    error_selector = ".alert-danger"
    success_indicator = "#receipt"  # Element indicating successful order placement
    page = browser.page()
    
    for order in orders:  # Now processes all orders
        order_number = str(order["Order number"])
        setup_order(page, order)
        
        placed_successfully = False
        while not placed_successfully:
            page.click('//*[@id="order"]')  # Attempt to place the order
            sleep(2)  # Short delay to allow for page response

            if page.is_visible(success_indicator, timeout=10000):
                print(f"Order {order_number} placed successfully.")
                finalize_order(page, order_number)
                placed_successfully = True
            elif page.is_visible(error_selector, timeout=5000):
                print(f"Error placing order {order_number}. Retrying...")
                # Handle specific error conditions here if necessary before retrying
                # For example, check if an error message indicates a retry is not possible
                continue
            else:
                print(f"Order {order_number} status unclear. Retrying...")
                # Optional: Implement additional checks or conditions here
            
        reset_form_for_next_order(page)


def finalize_order(page, order_number):
    """Handles operations after successful order placement, like saving receipt and taking screenshots."""
    pdf_filename = store_receipt_as_pdf(order_number)
    screen_shot_file_name = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screen_shot_file_name, pdf_filename)
    # Prepare for the next order, if applicable
    reset_form_for_next_order(page)

# Implement reset_form_for_next_order, store_receipt_as_pdf, screenshot_robot, and any other necessary functions here


def setup_order(page, order):
    """Fill in the order form based on the provided order details."""
    page.select_option("#head", str(order["Head"]))
    page.click(f'//*[@id="id-body-{str(order["Body"])}"]')
    page.fill('input.form-control[type="number"][min="1"][max="6"][placeholder="Enter the part number for the legs"]', str(order["Legs"]))
    page.fill('#address', str(order["Address"]))
    page.click('text=Preview')

def retry_order_placement(page, error_selector):
    """Attempt to click the order button again and verify success."""
    page.click('//*[@id="order"]')
    # Optionally wait for a condition that confirms the order went through or the error was resolved
    if not page.is_visible(error_selector, timeout=5000):
        print("Succesfully placed order after RETRY!")
    else:
        print("Retry failed, error still present.")



def reset_form_for_next_order(page):
    """Click 'Order another robot' to reset the form, if the button is visible."""
    if page.is_visible('text=Order another robot', timeout=3000):
        page.click('text=Order another robot')
    close_annoying_modal()

def close_annoying_modal():
    """Close any modal dialog, if open."""
    page = browser.page()
    if page.is_visible("text=OK", timeout=3000):
        page.click("text=OK")



def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    screenshots_dir = Path("output/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    
    page = browser.page()
    filename = screenshots_dir / f"{order_number}_screenshot_robot.png"
    element = page.locator('#robot-preview-image')
    element.screenshot(path=str(filename))  # Ensure the path is converted to string if necessary
    
    return filename




def store_receipt_as_pdf(order):
    """Stores the receipt as a PDF file"""
    receipts_dir = Path("output/receipts")
    receipts_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    
    page = browser.page()
    results_html = page.locator("#receipt").inner_html()
    pdf_filename = receipts_dir / f"{order}_store_receipt.pdf"
    pdf.html_to_pdf(results_html, str(pdf_filename))  # Ensure the path is converted to string if necessary
    
    return pdf_filename




def archive_receipts():
    # Assuming your PDF files are stored in a directory named 'receipts'
    output_dir = Path("output")
    receipts_dir = output_dir / "receipts"
    screenshots_dir = output_dir / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists

    # Create a ZIP archive of the receipts directory
    archive_path = shutil.make_archive(output_dir / "receipts_archive", "zip", root_dir=receipts_dir)
    print(f"Archive created at: {archive_path}")



def embed_screenshot_to_receipt(screenshot, pdf_file):
    # Append the screenshot to the specified PDF file
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def get_orders():
  
    tables = Tables()

    # Define the path to your CSV file
    csv_file_path = "orders.csv"

    # Read the CSV file into a table
    table = tables.read_table_from_csv(csv_file_path, header=True)
    return table
 

def open_robot_order_website():
    browser.goto(website)







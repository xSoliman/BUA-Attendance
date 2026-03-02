"""
QR Code Generator for Student Attendance Cards

This script generates QR codes for students from a CSV file. Each QR code
contains the student's ID and includes a footer with the student's name
and ID for easy identification.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6

Usage:
    python generate_qr.py <csv_file_path>

Example:
    python generate_qr.py students.csv

CSV Format:
    Student_ID,Name
    20210001,Ahmed Mohamed
    20210002,Sara Ali
"""

import sys
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import pandas as pd


def create_output_directory(output_dir="output"):
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory
        
    Requirements: 10.6
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")


def generate_qr_code(student_id):
    """
    Generate a QR code image for a student ID.
    
    Args:
        student_id: The student's unique identifier
        
    Returns:
        PIL.Image: QR code image
        
    Requirements: 10.2, 10.3
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size (1 is smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )
    
    # Add student ID data to QR code
    qr.add_data(str(student_id))
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    return qr_image


def add_footer_to_image(qr_image, student_name, student_id):
    """
    Add a text footer to the QR code image with student information.
    
    Args:
        qr_image: PIL Image of the QR code
        student_name: Student's name
        student_id: Student's ID
        
    Returns:
        PIL.Image: QR code image with footer
        
    Requirements: 10.4
    """
    # Convert QR image to RGB if needed
    if qr_image.mode != 'RGB':
        qr_image = qr_image.convert('RGB')
    
    # Calculate dimensions
    qr_width, qr_height = qr_image.size
    footer_height = 60
    total_height = qr_height + footer_height
    
    # Create new image with space for footer
    final_image = Image.new('RGB', (qr_width, total_height), 'white')
    
    # Paste QR code at the top
    final_image.paste(qr_image, (0, 0))
    
    # Draw footer text
    draw = ImageDraw.Draw(final_image)
    
    # Try to use a nice font, fall back to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
    
    # Footer text
    footer_text = f"Name: {student_name} | ID: {student_id}"
    
    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), footer_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + 20
    
    # Draw text
    draw.text((text_x, text_y), footer_text, fill='black', font=font)
    
    return final_image


def process_csv(csv_file_path, output_dir="output"):
    """
    Process CSV file and generate QR codes for all students.
    
    Args:
        csv_file_path: Path to the CSV file containing student data
        output_dir: Directory to save generated QR codes
        
    Requirements: 10.1, 10.2, 10.5, 10.6
    """
    # Validate CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found: {csv_file_path}")
        sys.exit(1)
    
    # Create output directory
    create_output_directory(output_dir)
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Validate required columns
    required_columns = ['Student_ID', 'Name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Error: CSV file is missing required columns: {missing_columns}")
        print(f"Required columns: {required_columns}")
        print(f"Found columns: {list(df.columns)}")
        sys.exit(1)
    
    # Generate QR codes for each student
    print(f"Generating QR codes for {len(df)} students...")
    
    for index, row in df.iterrows():
        student_id = str(row['Student_ID']).strip()
        student_name = str(row['Name']).strip()
        
        # Skip empty rows
        if not student_id or student_id == 'nan':
            continue
        
        try:
            # Generate QR code
            qr_image = generate_qr_code(student_id)
            
            # Add footer with student information
            final_image = add_footer_to_image(qr_image, student_name, student_id)
            
            # Save image with filename format: {Student_ID}.png
            output_path = os.path.join(output_dir, f"{student_id}.png")
            final_image.save(output_path)
            
            print(f"✓ Generated QR code for {student_name} ({student_id})")
            
        except Exception as e:
            print(f"✗ Error generating QR code for {student_name} ({student_id}): {e}")
    
    print(f"\nDone! QR codes saved to: {output_dir}/")


def main():
    """
    Main entry point for the QR code generator script.
    """
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_qr.py <csv_file_path>")
        print("\nExample:")
        print("  python generate_qr.py students.csv")
        print("\nCSV Format:")
        print("  Student_ID,Name")
        print("  20210001,Ahmed Mohamed")
        print("  20210002,Sara Ali")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    # Optional: custom output directory
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    # Process CSV and generate QR codes
    process_csv(csv_file_path, output_dir)


if __name__ == "__main__":
    main()

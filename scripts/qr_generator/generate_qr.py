"""
QR Code Generator for Student Attendance Cards

This script generates QR codes for students from Excel/CSV files in the input directory.
Each QR code contains the student's name and ID, with a footer for easy identification.

Supports Arabic text in student names.
Processes all tabs/sheets in Excel files automatically.
Organizes output by Sheet/Tab/Group/Section hierarchy.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6

Usage:
    python generate_qr.py <sheet_name>

Examples:
    python generate_qr.py AI
    python generate_qr.py AS-B7
    python generate_qr.py Logic_sheet

Directory Structure:
    input/          - Place your Excel/CSV files here
    output/         - Generated QR codes organized by Sheet/Tab/Section
        AI/
            TabName1/
                A1/
                    20210001.png
                    20210002.png
                A2/
            TabName2/
                B1/

File Format (required columns):
    ID,Name,Section
    20210001,Ahmed Mohamed,A1
    20210002,Sara Ali,A2
    20210003,أحمد محمد,B1

Note: CSV files should be saved with UTF-8 encoding to support Arabic text.
"""

import sys
import os
import re
import qrcode
from PIL import Image, ImageDraw, ImageFont
import pandas as pd


def get_script_directory():
    """Get the directory where the script is located."""
    return os.path.dirname(os.path.abspath(__file__))


def create_output_directory(output_dir):
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory
        
    Requirements: 10.6
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def extract_group_from_section(section):
    """
    Extract the group letter from a section code.
    
    Examples:
        A1 -> A
        B5 -> B
        A -> A
        
    Args:
        section: Section code (e.g., "A1", "B5")
        
    Returns:
        Group letter (e.g., "A", "B")
    """
    # Extract the first letter(s) before any digits
    match = re.match(r'^([A-Za-z]+)', str(section).strip())
    if match:
        return match.group(1).upper()
    return "Unknown"


def generate_qr_code(student_id, student_name=None):
    """
    Generate a QR code image for a student.
    
    Args:
        student_id: The student's unique identifier
        student_name: The student's name (optional, for enhanced QR data)
        
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
    
    # Add student data to QR code
    # Format: "Name - ID" if name provided, otherwise just ID
    if student_name:
        qr_data = f"{student_name} - {student_id}"
    else:
        qr_data = str(student_id)
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    return qr_image


def add_footer_to_image(qr_image, student_name, student_id):
    """
    Add a text footer to the QR code image with student information.
    Supports Arabic text rendering.
    
    Args:
        qr_image: PIL Image of the QR code
        student_name: Student's name (supports Arabic)
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
    footer_height = 80  # Increased for better Arabic text display
    total_height = qr_height + footer_height
    
    # Create new image with space for footer
    final_image = Image.new('RGB', (qr_width, total_height), 'white')
    
    # Paste QR code at the top
    final_image.paste(qr_image, (0, 0))
    
    # Draw footer text
    draw = ImageDraw.Draw(final_image)
    
    # Try to load fonts that support Arabic
    font = None
    arabic_fonts = [
        # Linux fonts
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        # Windows fonts
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
        # macOS fonts
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    
    for font_path in arabic_fonts:
        try:
            font = ImageFont.truetype(font_path, 16)  # Increased size for better readability
            break
        except:
            continue
    
    # Fallback to default font if no TrueType font found
    if font is None:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Footer text - name on first line, ID on second line for better Arabic display
    name_text = f"{student_name}"
    id_text = f"ID: {student_id}"
    
    # Calculate text positions (centered)
    if font:
        # Name text (first line)
        name_bbox = draw.textbbox((0, 0), name_text, font=font)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (qr_width - name_width) // 2
        name_y = qr_height + 15
        
        # ID text (second line)
        id_bbox = draw.textbbox((0, 0), id_text, font=font)
        id_width = id_bbox[2] - id_bbox[0]
        id_x = (qr_width - id_width) // 2
        id_y = qr_height + 40
        
        # Draw text
        draw.text((name_x, name_y), name_text, fill='black', font=font)
        draw.text((id_x, id_y), id_text, fill='black', font=font)
    else:
        # Fallback without font
        combined_text = f"{student_name} | ID: {student_id}"
        text_y = qr_height + 25
        draw.text((10, text_y), combined_text, fill='black')
    
    return final_image


def process_sheet_data(df, sheet_name, tab_name, output_base_dir):
    """
    Process a single sheet/tab and generate QR codes for all students.
    
    Args:
        df: DataFrame containing student data
        sheet_name: Name of the file (without extension)
        tab_name: Name of the tab/sheet within the file
        output_base_dir: Base output directory
        
    Returns:
        Tuple of (success_count, error_count)
    """
    # Validate required columns
    id_column = None
    if 'Student_ID' in df.columns:
        id_column = 'Student_ID'
    elif 'ID' in df.columns:
        id_column = 'ID'
    else:
        print(f"  ⚠ Skipping tab '{tab_name}': Missing ID column")
        print(f"     Found columns: {list(df.columns)}")
        return (0, 0)
    
    if 'Name' not in df.columns:
        print(f"  ⚠ Skipping tab '{tab_name}': Missing 'Name' column")
        print(f"     Found columns: {list(df.columns)}")
        return (0, 0)
    
    if 'Section' not in df.columns:
        print(f"  ⚠ Skipping tab '{tab_name}': Missing 'Section' column")
        print(f"     Found columns: {list(df.columns)}")
        return (0, 0)
    
    print(f"\n  Processing tab: {tab_name}")
    print(f"  Using column '{id_column}' for student IDs")
    print(f"  Found {len(df)} rows")
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        student_id = str(row[id_column]).strip()
        student_name = str(row['Name']).strip()
        section = str(row['Section']).strip()
        
        # Skip empty rows
        if not student_id or student_id == 'nan':
            continue
        
        if not section or section == 'nan':
            print(f"    ⚠ Skipping {student_name} ({student_id}): No section")
            continue
        
        try:
            # Extract group from section (for display purposes only)
            group = extract_group_from_section(section)
            
            # Create output directory: output/SheetName/TabName/Section/
            output_dir = os.path.join(output_base_dir, sheet_name, tab_name, section)
            create_output_directory(output_dir)
            
            # Generate QR code
            qr_image = generate_qr_code(student_id, student_name)
            final_image = add_footer_to_image(qr_image, student_name, student_id)
            
            # Save image
            output_path = os.path.join(output_dir, f"{student_id}.png")
            final_image.save(output_path)
            
            success_count += 1
            print(f"    ✓ {student_name} ({student_id}) -> {tab_name}/{section}/")
            
        except Exception as e:
            error_count += 1
            print(f"    ✗ Error: {student_name} ({student_id}): {e}")
    
    return (success_count, error_count)


def process_file(sheet_name):
    """
    Process Excel or CSV file from input directory and generate QR codes for all students.
    For Excel files, processes all tabs/sheets.
    Organizes output by Sheet/Tab/Section hierarchy.
    
    Args:
        sheet_name: Name of the sheet file (without extension)
        
    Requirements: 10.1, 10.2, 10.5, 10.6
    """
    script_dir = get_script_directory()
    input_dir = os.path.join(script_dir, "input")
    output_base_dir = os.path.join(script_dir, "output")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found: {input_dir}")
        print("Please create an 'input' directory and place your files there.")
        sys.exit(1)
    
    # Find the file in input directory
    file_path = None
    for ext in ['.xlsx', '.xls', '.csv']:
        potential_path = os.path.join(input_dir, f"{sheet_name}{ext}")
        if os.path.exists(potential_path):
            file_path = potential_path
            break
    
    if not file_path:
        print(f"Error: File not found in input directory: {sheet_name}")
        print(f"Looked for: {sheet_name}.xlsx, {sheet_name}.xls, {sheet_name}.csv")
        print(f"\nAvailable files in input directory:")
        if os.path.exists(input_dir):
            files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
            if files:
                for f in files:
                    print(f"  - {f}")
            else:
                print("  (no files found)")
        sys.exit(1)
    
    # Detect file type
    file_extension = os.path.splitext(file_path)[1].lower()
    
    print(f"{'='*60}")
    print(f"Processing: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    total_success = 0
    total_errors = 0
    
    try:
        if file_extension in ['.xlsx', '.xls']:
            # Read Excel file - get all sheet names first
            excel_file = pd.ExcelFile(file_path, engine='openpyxl' if file_extension == '.xlsx' else None)
            sheet_names = excel_file.sheet_names
            
            print(f"\nFound {len(sheet_names)} tab(s) in Excel file:")
            for name in sheet_names:
                print(f"  - {name}")
            
            # Process each sheet/tab
            for tab_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=tab_name, engine='openpyxl' if file_extension == '.xlsx' else None)
                    success, errors = process_sheet_data(df, sheet_name, tab_name, output_base_dir)
                    total_success += success
                    total_errors += errors
                except Exception as e:
                    print(f"\n  ✗ Error processing tab '{tab_name}': {e}")
                    total_errors += 1
            
        elif file_extension == '.csv':
            # Read CSV file
            print(f"\nReading CSV file...")
            try:
                df = pd.read_csv(file_path, encoding='utf-8', quoting=1)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig', quoting=1)
                except:
                    df = pd.read_csv(file_path, encoding='cp1256', quoting=1)
            
            # Process as single sheet (CSV has no tabs)
            success, errors = process_sheet_data(df, sheet_name, sheet_name, output_base_dir)
            total_success += success
            total_errors += errors
            
    except Exception as e:
        print(f"\nError reading file: {e}")
        print("\nPossible issues:")
        print("  1. File has inconsistent columns")
        print("  2. Excel file is corrupted or password-protected")
        print("  3. Missing required library (run: pip install openpyxl)")
        sys.exit(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"✓ Successfully generated: {total_success} QR codes")
    if total_errors > 0:
        print(f"✗ Errors: {total_errors}")
    print(f"\nOutput directory: {os.path.join(output_base_dir, sheet_name)}/")
    print(f"{'='*60}")


def main():
    """
    Main entry point for the QR code generator script.
    """
    # Check command line arguments
    if len(sys.argv) < 2:
        print("QR Code Generator for Student Attendance")
        print("=" * 60)
        print("\nUsage: python generate_qr.py <sheet_name>")
        print("\nExamples:")
        print("  python generate_qr.py AI")
        print("  python generate_qr.py AS-B7")
        print("  python generate_qr.py Logic_sheet")
        print("\nDirectory Structure:")
        print("  input/          - Place your Excel/CSV files here")
        print("  output/         - Generated QR codes (Sheet/Tab/Section)")
        print("\nRequired File Format:")
        print("  Columns: ID, Name, Section")
        print("  Example:")
        print("    ID,Name,Section")
        print("    20210001,Ahmed Mohamed,A1")
        print("    20210002,Sara Ali,A2")
        print("    20210003,أحمد محمد,B1")
        print("\nSupported formats: .xlsx, .xls, .csv")
        print("\nNote: For Excel files, all tabs will be processed automatically")
        sys.exit(1)
    
    sheet_name = sys.argv[1]
    
    # Remove extension if provided
    sheet_name = os.path.splitext(sheet_name)[0]
    
    # Process file and generate QR codes
    process_file(sheet_name)


if __name__ == "__main__":
    main()

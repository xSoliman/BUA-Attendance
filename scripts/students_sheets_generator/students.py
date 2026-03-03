import csv
import sys
import os


def transform_csv(input_file, output_file=None):
    """
    Reads a CSV file with columns including 'First name', 'Last name', 'Username', 'ID number'
    and generates a new CSV with just 'ID' and 'Name' columns.
    ID is taken from 'ID number', falling back to 'Username' if empty.
    Output is saved to 'Students_sheets' directory beside the script.
    """
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}_sheet.csv"

    # Save output to 'Students_sheets' dir beside the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "Students_sheets")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(output_file))

    with open(input_file, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        # Validate required columns exist
        required_cols = {"First name", "Last name", "Username", "ID number"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        rows = []
        for row in reader:
            id_val = row["ID number"].strip() or row["Username"].strip()
            rows.append({
                "ID": id_val,
                "Name": f"{row['First name'].strip()} {row['Last name'].strip()}"
            })

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["ID", "Name"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! {len(rows)} records written to: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transform_csv.py <input.csv> [output.csv]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    transform_csv(input_path, output_path)

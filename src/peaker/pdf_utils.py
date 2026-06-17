"""Utilities to create a PDF report with plots and a table."""

import os
from dataclasses import dataclass
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from peaker.parse_xmls import Output


def _get_plt_path(plots, test_name, test_class):
    plt_name = None
    for plt in plots:
        plt_basename = os.path.basename(plt)
        if test_name in plt_basename and test_class in plt_basename:
            plt_name = plt
            break
    return plt_name


def _select_cols(report_table):
    # Select the columns and add the column name to later append the page numbers of the plot location
    selected_cols = []
    headers = ["Test Name", "Instrument Mode", "Units", "Latest Peak Mem",
               "Data Points", "End Median - Start Median", "Plot Page"]
    for i in range(len(report_table["Test_name"])):
        if i == 0:
            selected_cols.append(headers)
        row = [
            str(report_table["Test_name"][i]),
            str(report_table["Instrument_mode"][i]),
            str(report_table["Units"][i]),
            str(report_table["Latest_peakmem"][i]),
            str(report_table["Data_points"][i]),
            str(report_table["Diff_medians"][i]),
            ]
        selected_cols.append(row)

    # The table format for the PDF can adjust the column width size with a tuple
    # called col_widths. Each number is a percentage of the total page
    # width, and the tuple should add up to 100.
    col_widths = (37, 23, 7, 9, 8, 9, 7)

    # Sanity checks
    if len(headers) != len(col_widths):
        raise ValueError("Inconsistent number of columns and widths in PDF table.")
    if sum(col_widths) != 100:
        raise ValueError("Inconsistent column widths in PDF table.")
    
    return selected_cols, col_widths


@dataclass
class PdfData:
    """Structure containing PDF information."""
    pdf: FPDF
    output: Output
    classnames: str
    selected_cols: list
    page_counter: int


def _add_title(pdf_data, title, title_font, title_size):
    pdf_data.pdf.set_font(title_font, size=title_size)  # Set the font for text.
    pdf_data.pdf.multi_cell(w=0, h=10, text=title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")


def _add_figure(pdf_data, set_y, fig_text, mem_text, plt_xyw, table_entry):
    # These are all the cell parameters that can be modified:
    # Cell(width, height, text, border (0=no, 1=yes),
    #      new_x=XPos.RIGHT, new_y=YPos.TOP,    ->  Cursor stays to the right of the cell (same line)
    #      new_x=XPos.LMARGIN, new_y=YPos.NEXT, ->  Moves cursor to the start of the next line (left margin)
    #      new_x=XPos.LEFT, new_y=YPos.NEXT,  ->  Moves cursor directly below the current cell
    #      align ('L', 'C', 'R'))

    # Add the text for each plot
    pdf_data.pdf.set_y(set_y)
    text = "{}:  {}".format(fig_text, pdf_data.output.report_table["Test_name"][0])
    pdf_data.pdf.cell(w=0, h=10, text=text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    text = "  - Instrument mode:  {}".format(pdf_data.output.report_table["Instrument_mode"][0])
    pdf_data.pdf.cell(w=0, h=10, text=text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    text = " - {}:  {} {}".format(
        mem_text, pdf_data.output.report_table["Diff_medians"][0], pdf_data.output.report_table["Units"][0])
    pdf_data.pdf.cell(w=0, h=10, text=text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    # Get the plot name
    plt_name = _get_plt_path(pdf_data.output.plots, pdf_data.output.report_table["Test_name"][0],
                             pdf_data.classnames[0])

    # Add the image to the page
    pdf_data.pdf.image(plt_name, x=plt_xyw[0], y=plt_xyw[1], w=plt_xyw[2])

    # Update the table entry
    pdf_data.selected_cols[table_entry].append(str(pdf_data.page_counter))


def _add_page_number_and_increment(pdf_data):
    # Add the page number
    pdf_data.pdf.set_y(265)
    pdf_data.pdf.cell(200, 10, text=f"Page {pdf_data.page_counter}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # Increase the page counter
    pdf_data.page_counter += 1


def _add_table(pdf_data, col_widths, selected_cols):
    greyscale = 200
    with pdf_data.pdf.table(width=160, col_widths=col_widths,
                   cell_fill_color=greyscale, cell_fill_mode="ROWS") as table:
        for data_row in selected_cols:
            row = table.row()
            for datum in data_row:
                row.cell(datum)


def create_pdf(output, mission, py_version):
    """
    Creates a PDF report with plots and a table.
    
    Parameters
    ----------
    output : class
        A dataclass with the following elements:
        outdir - Full path for the output directory.
        tests_ran - Dictionary will have the test name are the keys and a subdictionary
            containing an array of dates, peak memory, and corresponding run times.
        local_sdate - Start date (Local time) for files with data.
        local_edate - End date (Local time) for files with data.
        report_table - Table of test data organized by test name and class.
        plots - List of plots.
    mission : str
        Mission name.
    py_version : str
        Version of Python tested and reported. 

    Returns
    -------
    Nothing
    
    """
    
    # Get selected data from table
    selected_cols, col_widths = _select_cols(output.report_table)
    try:
        classnames = output.report_table["Class"]
    except KeyError:
        classnames = output.report_table["Instrument_mode"]

    # Create an instance of an FPDF class.
    pdf = FPDF()

    # Define font type and size
    pdf_font = "Helvetica"
    main_title_font_size = 16
    sub_title_font_size = 13
    body_font_size = 9

    # Add content to the PDF

    # Start the dataclass for the PDF data
    page_counter = 1
    pdf_data = PdfData(pdf, output, classnames, selected_cols, page_counter)

    # Add first page and title of the PDF
    pdf.add_page()
    title = "{} Regression Tests Memory Peaks from \n {} to {}".format(
        mission.upper(), output.local_sdate, output.local_edate)
    _add_title(pdf_data, title, pdf_font, main_title_font_size)

    # Set up for the rest of the first page: worse performance, highest memory peak increment
    pdf.set_font(pdf_font, size=body_font_size)

    # highest memory peak
    set_y = 45
    fig_text = "Test with the highest memory peak **increment**"
    mem_text = "Memory Peak increased from beginning of period by"
    plt_xyw = [5, 80, 200]
    table_entry = 1
    _add_figure(pdf_data, set_y, fig_text, mem_text, plt_xyw, table_entry)
    _add_page_number_and_increment(pdf_data)

    # Second page: best performance, highest memory peak decrement
    pdf.add_page()
    set_y = 30
    fig_text = "Test with the highest memory peak **improvement**"
    mem_text = "Memory Peak decreased from beginning of period by"
    plt_xyw = [5, 70, 200]
    table_entry = -1
    _add_figure(pdf_data, set_y, fig_text, mem_text, plt_xyw, table_entry)
    _add_page_number_and_increment(pdf_data)

    # Pages with all other tests
    # Remember in the loop to exclude the first and last entries
    for i in range(1, len(output.report_table["Test_name"])-1, 2):
        pdf.add_page()
        table_row = i + 1

        # Only at top of the third page, add subtitle for the rest of the tests/plots
        if i == 1:
            # add subtitle
            pdf.set_y(18)
            text = "The following pages present other changes in memory peak"
            _add_title(pdf_data, text, pdf_font, sub_title_font_size)

            # Reset the font for the remainder of the file
            pdf.set_font(pdf_font, size=body_font_size)

        # Two plots per page from now-on

        # First plot in this page
        set_y = 30
        fig_text = "Test name"
        mem_text = "Peak memory change"
        plt_xyw = [65, 50, 115]
        table_entry = table_row
        _add_figure(pdf_data, set_y, fig_text, mem_text, plt_xyw, table_entry)

        # Second test plot in the same page
        if len(output.report_table["Test_name"])-1 > i + 1:
            set_y = 145
            plt_xyw = [65, 165, 115]
            table_entry = table_row + 1
            _add_figure(pdf_data, set_y, fig_text, mem_text, plt_xyw, table_entry)

        # Add page number and increase the page counter
        _add_page_number_and_increment(pdf_data)

    # Add table with plot names, page numbers, and other data
    pdf.add_page()
    pdf.set_y(30)
    _add_table(pdf_data, col_widths, selected_cols)

    # Output the PDF to a file.
    pdf_name = "report_peak_mem_" + py_version + ".pdf"
    pdf_path = output.outdir / pdf_name
    pdf.output(pdf_path)
    
    print("\nPDF generated successfully: {}".format(pdf_path))

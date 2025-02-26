import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import pdfplumber
import time
from fpdf import FPDF

# Set page configuration for better layout
st.set_page_config(page_title="TaxGPT", page_icon="📂", layout="wide")

#Define the logo image URL or file path
logo_path = "logo.png" 

# Sidebar layout with logo + title
with st.sidebar:
    col1, col2 = st.columns([1, 3])  # Adjust width ratios

    with col1:
        st.image(logo_path, width=50)

    with col2:
        st.markdown("<h1 style='color: lightgrey; font-size: 27px; margin-top: -27px;'>TaxGPT</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: lightgrey; font-size: 18px; margin-top: -13px;'>Simplifying Taxes, Maximising Clarity</p>", unsafe_allow_html=True)

    # 🚀 Shift Tabs Down by Wrapping in a Container
    st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)  
    
    def open_page(page_url):
        st.markdown(f"""
            <meta http-equiv="refresh" content="0; URL='{page_url}'">
        """, unsafe_allow_html=True)

    def clickable_tab(label, target_page=None):
        """Creates a full-width clickable tab between separators."""
        st.markdown("---")
        st.markdown(f"""
            <div onclick="window.location.href='{target_page if target_page else f'#{label}'}'" 
                 style="
                    padding: 15px;
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    cursor: pointer;
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                    transition: background-color 0.3s;" 
                onmouseover="this.style.backgroundColor='rgba(255, 255, 255, 0.8)'" 
                onmouseout="this.style.backgroundColor='rgba(255, 255, 255, 0.1)'">
                {label}
            </div>
        """, unsafe_allow_html=True)

    # Clickable sidebar tabs
    with st.sidebar:
        # Articles Tab with Dropdown
        #st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        with st.expander("📖 Recent Articles", expanded=True):  # Expander acts as a dropdown
            st.markdown('<a href="https://www.moneycontrol.com/news/business/personal-finance/here-s-how-the-new-income-tax-bill-will-change-the-rules-for-taxpayers-12949181.html" target="_blank">📄 Article 1: How the new Income Tax Bill will change the rules for taxpayers </a>', unsafe_allow_html=True)
            st.markdown('<a href="https://www.moneycontrol.com/news/business/personal-finance/tax-planning-for-2025-how-to-maximise-your-savings-before-march-31-deadline-12944450.html" target="_blank">📄 Article 2: Tax Planning Guide</a>', unsafe_allow_html=True)
            st.markdown('<a href="https://www.moneycontrol.com/news/business/personal-finance/new-income-tax-bill-section-80c-tax-saving-deductions-now-under-clause-123-12939798.html" target="_blank">📄 Article 3:  Section 80C tax-saving deductions now under clause 123</a>', unsafe_allow_html=True)

        st.markdown("---")

        with st.expander("📖 Try asking", expanded=True):
            st.markdown("Old Regime vs New Regime, best option for me?")
            st.markdown("How can I maximize my tax savings before the financial year ends?")
            st.markdown("How can I reduce my taxable income legally?")
            st.markdown("What are the best ways to invest for tax benefits under Section 80C?")
            st.markdown("What are the best investment options for tax-free returns?")
            st.markdown("Can I save taxes if I invest in my child's education?")

    # Initialize session state for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home" 


# Initialize Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def query_gemini(prompt):
    """Send a prompt to Gemini API and get a response."""
    model = genai.GenerativeModel("gemini-1.5-pro")  # Use Gemini Pro model
    response = model.generate_content(prompt)
    return response.text

def get_prompt(file_id, extracted_text):
    templates = {
        1: f""" You are a tax assistant. Your work is to analyze 
        and provide proper summary of Salary Slip provided in input.
        Provide the below mentioned information:
        - Company & Employee names along with addresses and other basic information.
        - Make proper tables for recording the earnings and deductions. Make tables for 
        any additional information provided (like employer contributions)
        - Simply, summarize the data at last and tell the salary one takes home.

        **Document Content:**
        {extracted_text}
        """,
        
        2: f"""
        You are a tax assistant. Your work is to analyze 
        and provide proper summary of Form 16 provided in input.
        Provide the below mentioned information:
        - Provide basic employee and employer details.
        - Provide PAN, TAN along with assessment year.
        - Make proper table of salary and tax deducted.
        - Make proper table of tax deposited.
        - Make proper table of Total salary (Gross Salary = Basic Salary + Allowances + Perks)
        - Make proper table of Exemptions/Allowances then calculate "Taxable Salary".
        - Make proper table of Deductions then calculate "Taxable Income".
        - Calculate tax on the total taxable income by showing how tax
        is applied accross various slabs of income.
        - Finally provide basic information like, "Total Tax Payable 
        (before Cess)", "Total Tax Payable (after Cess)", "TDS Deducted",
        "Tax Refund Due".
        -Properly, segregate the Part A and B of form.
        
        **Document Content:**
        {extracted_text}
        """,
        
        3: f"""
        You are a tax assistant. Your work is to analyze 
        and provide proper summary of Form 26AS provided in input.
        Provide the below mentioned information:
        - Mention the name and address of Assessee, PAN, Financial and Asessment
        year.
        - Make a proper table of tax deducted at source. (TDS)
        - Make a proper table of tax collected at source. (TCS) (Applicable in
        some cases only like purchasing property or car) (This table is optional)
        - Make a proper table of Tax paid (other than TDS or TCS). (Applicable in 
        cases of advance tax or self assessment tax or other direct tax payments) (This
        table is optional)
        - Give concise summary of "TDS Deducted & Deposited", "TCS Collected & Deposited"
        "Self-Assessment Tax Paid", "Total Tax Payments (TDS + TCS + Direct Tax)".
        
        **Document Content:**
        {extracted_text}
        """,
        
        4: f"""
        You are a tax assistant. Your work is to analyze 
        and provide proper summary of GST Bill (Tax Invoice) provided in input.
        Provide the below mentioned information:
        - Provide Company/Seller details like name, address, phone number, email, GSTIN etc.
        - Provide Bill To (Customer) details like above.
        - Make a proper table of Items purchased.
        - Then, show how the total amount was calculated by showing in very 
        short manner some calculations.
        
        **Document Content:**
        {extracted_text}
        """,
        
        5: f"""
        You are a tax assistant. Your work is to analyze 
        and provide proper summary of GSTR 3B provided in input.
        Provide the below mentioned information:
        - Provide Legal Name of the Registered Person along with GSTIN.
        - Make a proper table of Outward Supplies and Inward Supplies Liable
        to Reverse Charge then, calculate the "Total Taxable Turnover".
        - Make a proper table of Inter-State Supplies then, calculate "Total 
        Inter State Tax".
        - Make a proper table of Eligible Input Tax Credit (ITC) then, calculate
        " Final ITC Available".
        - Make a proper table of Value of Exempt, Nil-Rated & Non-GST Inward Supplies
        then, calculate "Total Exempt/Nil Supplies".
        - Make a proper table of Payment of Tax then, calculate "Total Tax Payable", 
        "Total Paid via ITC", "Total Paid via Cash/TDS".
        - Make a proper table of TDS/TCS Credit then, calculate "Total TDS/TCS Credit" (Formula
        is sum of Integrated Tax).
        - Provide the final summary: "Total Taxable Value (Outward + Reverse Charge)", "Total ITC 
        Available", "Total Tax Payable", "Paid via ITC", "Paid via Cash/TDS", "TDS/TCS Credit Used".

        **Document Content:**
        {extracted_text}
        """
    }
    return templates.get(file_id, "Invalid document type.")

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "document_results" not in st.session_state:
    st.session_state.document_results = {}  # Store LLM results

# Function to switch pages
def go_to_processing():
    st.session_state.page = "processing"
    st.rerun()

def go_to_results():
    st.session_state.page = "results"
    st.rerun()

# -------------------- PAGE 1: FILE UPLOAD --------------------
if st.session_state.page == "upload":
    st.title("Upload your official documents")

    col1 = st.columns([1])[0]
    col2 = st.columns([1])[0]
    col3 = st.columns([1])[0]
    col4 = st.columns([1])[0]
    col5 = st.columns([1])[0]
    col6 = st.columns([1])[0]

    # Uploaders
    uploaded_files = [
        col1.file_uploader("Upload Salary Slip", type=["pdf"], key="file1"),
        col2.file_uploader("Upload Form 16", type=["pdf"], key="file2"),
        col3.file_uploader("Upload Form 26AS ", type=["pdf"], key="file3"),
        col4.file_uploader("Upload GST Bill (Tax Invoice)", type=["pdf"], key="file4"),
        col5.file_uploader("Upload GSTR 3B", type=["pdf"], key="file5"),
    ]

    with col6:
        analyze_button = st.button("Analyze", help="Click to process all uploaded documents")

    if analyze_button:
        # Store uploaded files in session state
        st.session_state.uploaded_files = uploaded_files
        go_to_processing()  # Move to processing screen

# -------------------- PAGE 2: PROCESSING SCREEN --------------------
if st.session_state.page == "processing":
    st.title("⏳ Processing Your Documents...")
    st.write("Your documents are being analyzed. Please wait while the AI processes the information.")
    
    with st.spinner("Processing... This may take a few moments."):
        time.sleep(5)  # Simulating processing delay

        # Process files one by one
        for i, uploaded_file in enumerate(st.session_state.uploaded_files, start=1):
            if uploaded_file:
                extracted_text = extract_text_from_pdf(uploaded_file)
                llm_prompt = get_prompt(i, extracted_text)
                response = query_gemini(llm_prompt)
                st.session_state.document_results[f"Document {i}"] = response  # Store result
        
    go_to_results()  # Move to results page

# -------------------- PAGE 3: DISPLAY RESULTS IN TABS --------------------
def generate_pdf(document_name, text):
    """Generates a PDF file from the provided text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Load Unicode Font (Make sure the file exists in the path)
    font_path = "H:\Google Girl Hackathon 2025\dejavu-sans\DejaVuSans.ttf"  # Update with the correct path
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)
    
    # Encode text to UTF-8 before writing
    pdf.multi_cell(0, 10, text.encode("utf-8", "ignore").decode("utf-8"))
    
    # Save PDF as bytes
    pdf_output = f"{document_name}.pdf"
    pdf.output(pdf_output, "F")
    return pdf_output

# Ensure page state is initialized
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Store chat messages

if st.session_state.page == "results":
    st.title("Analysis Results")

    tabs = st.tabs(["Salary Slip", "Form 16", "Form 26AS", "GST Bill (Tax Invoice)", "GSTR 3B"])
    
    # Display results in tabs
    for i, tab in enumerate(tabs, start=1):
        with tab:
            document_key = f"Document {i}"
            
            if document_key in st.session_state.document_results:
                response_text = st.session_state.document_results[document_key]
                st.write(response_text)
                
                # Generate PDF and provide a download button
                pdf_filename = generate_pdf(f"Analysis_{document_key}", response_text)
                
                with open(pdf_filename, "rb") as file:
                    st.download_button(
                        label="Download Analysis as PDF",
                        data=file,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
            else:
                st.write("No document uploaded for this category.")

    # Add a Chat Section for Doubts
    st.divider()
    st.subheader("💬 Have any doubts? Ask our AI Tax Assistant!")

    # Display previous chat history
    for chat in st.session_state.chat_history:
        st.write(f"🧑‍💻 **You:** {chat['user']}")
        st.write(f"🤖 **Tax Assistant:** {chat['bot']}")

    if "user_question" not in st.session_state:
        st.session_state["user_question"] = ""

    # User input for chat
    user_query = st.text_input("Ask a question about your tax document:", key="user_question")

    if st.button("Send"):
        if user_query:
            # Send query to LLM
            bot_response = query_gemini(user_query)

            # Store chat history
            st.session_state.chat_history.append({"user": user_query, "bot": bot_response})

            # Refresh page to display the new response
            st.rerun()

    if st.button("Go Back"):
        st.session_state.page = "upload"
        st.rerun()
       




    










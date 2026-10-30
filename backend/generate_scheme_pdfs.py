import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Nirmala font for Indian script / Kannada rendering
FONT_PATH = "C:/Windows/Fonts/Nirmala.ttc"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Nirmala", FONT_PATH, subfontIndex=0))
    FONT_NAME = "Nirmala"
else:
    FONT_NAME = "Helvetica"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheme_documents")
os.makedirs(OUT_DIR, exist_ok=True)

def get_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1b5e20"),
        alignment=1, # Center
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2e7d32"),
        alignment=1,
        spaceAfter=10
    )
    heading_style = ParagraphStyle(
        "DocHeading",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0d47a1"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#212121"),
        spaceAfter=4
    )
    kn_style = ParagraphStyle(
        "DocBodyKn",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#37474f"),
        spaceAfter=6
    )
    header_tag = ParagraphStyle(
        "HeaderTag",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#757575"),
        spaceAfter=6
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "heading": heading_style,
        "body": body_style,
        "kn": kn_style,
        "tag": header_tag
    }

def create_pm_kisan_pdf():
    pdf_path = os.path.join(OUT_DIR, "PM_KISAN_Operational_Guidelines.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    s = get_styles()
    story = []

    # PAGE 1
    story.append(Paragraph("GOVERNMENT OF INDIA - MINISTRY OF AGRICULTURE & FARMERS WELFARE", s["tag"]))
    story.append(Paragraph("<b>Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) - Operational Guidelines</b>", s["title"]))
    story.append(Paragraph("ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (ಪಿಎಂ-ಕಿಸಾನ್) ಅಧಿಕೃತ ಕಾರ್ಯಾಚರಣಾ ಮಾರ್ಗಸೂಚಿಗಳು", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Scheme Overview & Objective / ಯೋಜನೆಯ ಉದ್ದೇಶ</b>", s["heading"]))
    story.append(Paragraph("The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a Central Sector Scheme designed to supplement the financial needs of landholding farmers across India, including Karnataka, in procuring various inputs to ensure proper crop health and appropriate yields, commensurate with anticipated farm income at the end of each crop cycle.", s["body"]))
    story.append(Paragraph("ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆಯು ಭಾರತ ಸರ್ಕಾರದ ಪ್ರಮುಖ ಕೇಂದ್ರ ಪುರಸ್ಕೃತ ಯೋಜನೆಯಾಗಿದ್ದು, ಕರ್ನಾಟಕ ಸೇರಿದಂತೆ ದೇಶದ ಎಲ್ಲಾ ಕೃಷಿ ಭೂಮಿ ಹೊಂದಿರುವ ಅರ್ಹ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ಕೃಷಿ ಪರಿಕರಗಳ ಖರೀದಿ ಮತ್ತು ಕೃಷಿ ವೆಚ್ಚಗಳನ್ನು ಭರಿಸಲು ಆರ್ಥಿಕ ನೆರವು ಒದಗಿಸುತ್ತದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Financial Benefit & Payment Mechanism / ಆರ್ಥಿಕ ನೆರವು ಮತ್ತು ಪಾವತಿ ವಿಧಾನ</b>", s["heading"]))
    story.append(Paragraph("Under PM-KISAN, an annual financial benefit of <b>Rs 6,000 (Rupees Six Thousand)</b> per year is provided to all eligible landholder farmer families. The amount is released in <b>three equal four-monthly installments of Rs 2,000 each</b>: Period 1 (April to July), Period 2 (August to November), and Period 3 (December to March). Financial assistance is directly transferred into the bank accounts of the beneficiaries through Direct Benefit Transfer (DBT) and Aadhaar Payment Bridge (APB) system without any intermediaries.", s["body"]))
    story.append(Paragraph("ಅರ್ಹ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ಪ್ರತಿ ವರ್ಷಕ್ಕೆ ಒಟ್ಟು <b>₹6,000 (ಆರು ಸಾವಿರ ರೂಪಾಯಿ)</b> ಆರ್ಥಿಕ ನೆರವನ್ನು ತಲಾ ₹2,000 ರಂತೆ 3 ಸಮಾನ ಕಂತುಗಳಲ್ಲಿ ನೇರ ನಗದು ವರ್ಗಾವಣೆ (DBT) ಮೂಲಕ ರೈತರ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ನೇರವಾಗಿ ಜಮೆ ಮಾಡಲಾಗುತ್ತದೆ.", s["kn"]))

    story.append(Paragraph("<b>3. Definition of Eligible Beneficiary Family / ಅರ್ಹ ಫಲಾನುಭವಿ ಕುಟುಂಬದ ವ್ಯಾಖ್ಯಾನ</b>", s["heading"]))
    story.append(Paragraph("A landholder farmer family is defined as a family consisting of husband, wife, and minor children who own cultivable land as per the land records of Karnataka (Bhoomi RTC / Record of Rights, Tenancy and Crops). There is no restriction on maximum land ceiling; small, marginal, and large farmers holding valid registered land in Karnataka are eligible.", s["body"]))
    story.append(Paragraph("ಅರ್ಹ ರೈತ ಕುಟುಂಬ ಎಂದರೆ ಪತಿ, ಪತ್ನಿ ಮತ್ತು ಅಪ್ರಾಪ್ತ ಮಕ್ಕಳನ್ನು ಒಳಗೊಂಡ ಕುಟುಂಬವಾಗಿದ್ದು, ಕರ್ನಾಟಕ ಭೂಮಿ ತಂತ್ರಾಂಶದ ಅಧಿಕೃತ ಪಹಣಿ (RTC) ಪ್ರಕಾರ ತಮ್ಮ ಹೆಸರಿನಲ್ಲಿ ಸಾಗುವಳಿ ಮಾಡಬಹುದಾದ ಜಮೀನು ಹೊಂದಿರಬೇಕು.", s["kn"]))

    story.append(PageBreak())

    # PAGE 2
    story.append(Paragraph("GOVERNMENT OF INDIA - MINISTRY OF AGRICULTURE & FARMERS WELFARE | EXCLUSION CRITERIA", s["tag"]))
    story.append(Paragraph("<b>PM-KISAN Operational Guidelines - Strict Exclusion Criteria</b>", s["title"]))
    story.append(Paragraph("ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆ - ಕಡ್ಡಾಯ ಅನರ್ಹತೆ ಮತ್ತು ಹೊರಗಿಡುವಿಕೆ ನಿಯಮಗಳು", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c62828"), spaceAfter=10))

    story.append(Paragraph("<b>1. Mandatory Exclusion Categories / ಯೋಜನೆಯಿಂದ ಹೊರಗಿಡಲಾದ ವರ್ಗಗಳು</b>", s["heading"]))
    story.append(Paragraph("To ensure assistance reaches genuine cultivators, the following categories of beneficiaries of higher economic status are <b>STRICTLY INELIGIBLE</b> for benefits under PM-KISAN:", s["body"]))

    story.append(Paragraph("<b>Category A: Institutional Landholders</b><br/>All institutional landholders, trust lands, temple endowments, and agricultural companies are completely excluded.", s["body"]))
    story.append(Paragraph("ಸಂಸ್ಥಾಗತ ಭೂಮಾಲೀಕರು, ಟ್ರಸ್ಟ್, ದೇವಸ್ಥಾನದ ಜಮೀನು ಮತ್ತು ಕಂಪನಿಗಳು ಈ ಯೋಜನೆಗೆ ಅನರ್ಹವಾಗಿವೆ.", s["kn"]))

    story.append(Paragraph("<b>Category B: Constitutional Post Holders & Political Representatives</b><br/>Former and present holders of constitutional posts; former and present Ministers, State Ministers, Members of Lok Sabha, Rajya Sabha, State Legislative Assemblies (MLA), State Legislative Councils (MLC), Mayors of Municipal Corporations, and Chairpersons of District Panchayats.", s["body"]))
    story.append(Paragraph("ಸಾಂವಿಧಾನಿಕ ಹುದ್ದೆಗಳನ್ನು ಹೊಂದಿರುವವರು, ಮಾಜಿ ಮತ್ತು ಹಾಲಿ ಸಚಿವರು, ಸಂಸದರು (MP), ಶಾಸಕರು (MLA), ವಿಧಾನ ಪರಿಷತ್ ಸದಸ್ಯರು (MLC), ಮಹಾನಗರ ಪಾಲಿಕೆ ಮೇಯರ್‌ಗಳು ಮತ್ತು ಜಿಲ್ಲಾ ಪಂಚಾಯತ್ ಅಧ್ಯಕ್ಷರು ಅನರ್ಹರು.", s["kn"]))

    story.append(Paragraph("<b>Category C: Government Employees & High Pensioners</b><br/>All serving or retired officers and employees of Central/State Government Ministries, Departments, and field units, Central/State PSUs and autonomous bodies, local bodies (excluding Multi-Tasking Staff / Class IV / Group D employees). All superannuated/retired pensioners whose monthly pension is <b>Rs 10,000 or more</b> (excluding Group D pensioners).", s["body"]))
    story.append(Paragraph("ಸರ್ಕಾರಿ ನೌಕರರು, ಸಾರ್ವಜನಿಕ ವಲಯದ ಉದ್ಯೋಗಿಗಳು ಹಾಗೂ ಮಾಸಿಕ ₹10,000 ಕ್ಕಿಂತ ಹೆಚ್ಚು ಪಿಂಚಣಿ ಪಡೆಯುವ ನಿವೃತ್ತ ನೌಕರರು (ಗ್ರೂಪ್-ಡಿ ನೌಕರರನ್ನು ಹೊರತುಪಡಿಸಿ) ಅನರ್ಹರು.", s["kn"]))

    story.append(Paragraph("<b>Category D: Income Tax Payees & Registered Professionals</b><br/>All persons who paid Income Tax in the last assessment year. All professionals like Doctors, Engineers, Lawyers, Chartered Accountants (CA), and Architects registered with professional bodies and carrying on profession.", s["body"]))
    story.append(Paragraph("ಕಳೆದ ಮೌಲ್ಯಮಾಪನ ವರ್ಷದಲ್ಲಿ ಆದಾಯ ತೆರಿಗೆ (Income Tax) ಪಾವತಿಸಿದ ವ್ಯಕ್ತಿಗಳು ಮತ್ತು ನೋಂದಾಯಿತ ವೈದ್ಯರು, ಎಂಜಿನಿಯರ್‌ಗಳು, ವಕೀಲರು, ಲೆಕ್ಕ ಪರಿಶೋಧಕರು (CA) ಅನರ್ಹರು.", s["kn"]))

    story.append(PageBreak())

    # PAGE 3
    story.append(Paragraph("GOVERNMENT OF INDIA - MINISTRY OF AGRICULTURE & FARMERS WELFARE | APPLICATION & VERIFICATION", s["tag"]))
    story.append(Paragraph("<b>PM-KISAN - Registration Process, Documents & Verification</b>", s["title"]))
    story.append(Paragraph("ಪಿಎಂ-ಕಿಸಾನ್ - ನೋಂದಣಿ ವಿಧಾನ, ಅಗತ್ಯ ದಾಖಲೆಗಳು ಮತ್ತು ಪರಿಶೀಲನೆ", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Mandatory Documents Required / ಅಗತ್ಯವಿರುವ ಕಡ್ಡಾಯ ದಾಖಲೆಗಳು</b>", s["heading"]))
    story.append(Paragraph("1. <b>Aadhaar Card:</b> Mandatory Aadhaar card linked with active mobile number for OTP-based e-KYC or biometric e-KYC.<br/>"
                           "2. <b>Land Records (RTC / Pahani):</b> Updated Karnataka Bhoomi land record extract showing clear ownership, survey number, hissa, and extent of cultivable land in acres.<br/>"
                           "3. <b>Bank Account Details:</b> Aadhaar-seeded bank account with valid IFSC code (bank account must be active in PFMS DBT portal).<br/>"
                           "4. <b>Self-Declaration:</b> Affirmation that no family member falls under the exclusion list.", s["body"]))
    story.append(Paragraph("ಅಗತ್ಯ ದಾಖಲೆಗಳು: 1. ಆಧಾರ್ ಕಾರ್ಡ್ (ಇ-ಕೆವೈಸಿ ಕಡ್ಡಾಯ), 2. ಕರ್ನಾಟಕ ಭೂಮಿ ತಂತ್ರಾಂಶದ ಪಹಣಿ (RTC/ಪಹಣಿ), 3. ಆಧಾರ್ ಲಿಂಕ್ ಆಗಿರುವ ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್ ಮತ್ತು IFSC ಕೋಡ್, 4. ಮೊಬೈಲ್ ಸಂಖ್ಯೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Application Submission Workflow / ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ವಿಧಾನ</b>", s["heading"]))
    story.append(Paragraph("• <b>Online Portal:</b> Farmers can apply directly via the PM-KISAN official portal (pmkisan.gov.in) under 'Farmers Corner' -> 'New Farmer Registration'. Select Karnataka, District, Taluk, Hobli, Village, and input Land Survey Number.<br/>"
                           "• <b>In-Person Service Centers:</b> Farmers can visit the nearest Grama One Center, Karnataka Raitha Samparka Kendra (RSK), or Common Service Center (CSC) with documents.<br/>"
                           "• <b>e-KYC Mandatory:</b> Existing and new farmers must complete OTP or facial/biometric e-KYC to receive installments.", s["body"]))
    story.append(Paragraph("ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಅಧಿಕೃತ ಪೋರ್ಟಲ್ pmkisan.gov.in ಅಥವಾ ಸಮೀಪದ ಗ್ರಾಮ ಒನ್ (Grama One), ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಸಿಎಸ್‌ಸಿ ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.", s["kn"]))

    story.append(Paragraph("<b>3. Verification & Grievance Helpline / ಪರಿಶೀಲನೆ ಮತ್ತು ಸಹಾಯವಾಣಿ</b>", s["heading"]))
    story.append(Paragraph("Applications are scrutinized by the Village Accountant and Revenue Inspector, verified by the Taluk Tahsildar / Assistant Director of Agriculture, and approved by the State Nodal Department before DBT disbursement. For issues or status check, contact Karnataka PM-KISAN Helpline: <b>155261 / 1800-115-526</b>.", s["body"]))

    doc.build(story)
    print("Generated:", pdf_path)

def create_pmfby_pdf():
    pdf_path = os.path.join(OUT_DIR, "PMFBY_Karnataka_Samrakshane_Crop_Insurance.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    s = get_styles()
    story = []

    # PAGE 1
    story.append(Paragraph("GOVERNMENT OF KARNATAKA - DEPARTMENT OF AGRICULTURE & GOI", s["tag"]))
    story.append(Paragraph("<b>Pradhan Mantri Fasal Bima Yojana (PMFBY) - Karnataka Samrakshane</b>", s["title"]))
    story.append(Paragraph("ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (ಪಿಎಂಎಫ್‌ಬಿವೈ) - ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಮಾರ್ಗದರ್ಶಿ", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Scheme Objectives & Risk Coverage / ಯೋಜನೆಯ ಉದ್ದೇಶ ಮತ್ತು ರಕ್ಷಣೆ</b>", s["heading"]))
    story.append(Paragraph("The Pradhan Mantri Fasal Bima Yojana (PMFBY), integrated with Karnataka's state crop insurance portal 'Samrakshane', provides comprehensive risk insurance coverage for agricultural losses suffered by Karnataka farmers due to non-preventable natural perils: drought, dry spells, flood, inundation, widespread pests and plant diseases, landslides, natural fire and lightning, hailstorm, and cyclone.", s["body"]))
    story.append(Paragraph("ಪಿಎಂಎಫ್‌ಬಿವೈ ಯೋಜನೆಯು ನೈಸರ್ಗಿಕ ವಿಕೋಪಗಳಿಂದ (ಬರ, ಪ್ರವಾಹ, ಕೀಟಬಾಧೆ, ರೋಗ, ಆಲಿಕಲ್ಲು ಮಳೆ, ಅಕಾಲಿಕ ಮಳೆ) ಬೆಳೆ ನಷ್ಟ ಉಂಟಾದಾಗ ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಆರ್ಥಿಕ ನಷ್ಟ ಪರಿಹಾರ ಒದಗಿಸುವ ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ ಯೋಜನೆಯಾಗಿದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Farmer Premium Rates & Government Subsidies / ಪ್ರೀಮಿಯಂ ದರಗಳು</b>", s["heading"]))
    story.append(Paragraph("Farmers in Karnataka are required to pay only a minimal, highly subsidized premium rate as follows:<br/>"
                           "• <b>Kharif Food Crops & Oilseeds:</b> Maximum <b>2.0% of Sum Insured</b>.<br/>"
                           "• <b>Rabi Food Crops & Oilseeds:</b> Maximum <b>1.5% of Sum Insured</b>.<br/>"
                           "• <b>Annual Commercial & Horticultural Crops:</b> Maximum <b>5.0% of Sum Insured</b>.<br/>"
                           "The entire remaining actuarial premium balance is borne equally (50:50) by the Government of India and the Government of Karnataka, providing massive relief to farming families.", s["body"]))
    story.append(Paragraph("ರೈತರು ಪಾವತಿಸಬೇಕಾದ ಪ್ರೀಮಿಯಂ: 1. ಮುಂಗಾರು (Kharif) ಆಹಾರ ಮತ್ತು ಎಣ್ಣೆಕಾಳು ಬೆಳೆಗಳಿಗೆ: ಕೇವಲ <b>2.0%</b>, 2. ಹಿಂಗಾರು (Rabi) ಬೆಳೆಗಳಿಗೆ: ಕೇವಲ <b>1.5%</b>, 3. ವಾಣಿಜ್ಯ ಮತ್ತು ತೋಟಗಾರಿಕಾ ಬೆಳೆಗಳಿಗೆ: <b>5.0%</b>. ಉಳಿದ ಸಂಪೂರ್ಣ ಪ್ರೀಮಿಯಂ ಮೊತ್ತವನ್ನು ಕೇಂದ್ರ ಮತ್ತು ರಾಜ್ಯ ಸರ್ಕಾರಗಳು ಸಮಾನವಾಗಿ ಭರಿಸುತ್ತವೆ.", s["kn"]))

    story.append(PageBreak())

    # PAGE 2
    story.append(Paragraph("GOVERNMENT OF KARNATAKA - SAMRAKSHANE PORTAL | CROPS & ELIGIBILITY", s["tag"]))
    story.append(Paragraph("<b>PMFBY Karnataka - Notified Crops, Coverage Units & Eligibility</b>", s["title"]))
    story.append(Paragraph("ಕರ್ನಾಟಕದಲ್ಲಿ ಅಧಿಸೂಚಿತ ಬೆಳೆಗಳು, ವಿಮಾ ವ್ಯಾಪ್ತಿ ಮತ್ತು ರೈತರ ಅರ್ಹತೆ", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d47a1"), spaceAfter=10))

    story.append(Paragraph("<b>1. Major Notified Crops across Karnataka Districts / ಅಧಿಸೂಚಿತ ಬೆಳೆಗಳು</b>", s["heading"]))
    story.append(Paragraph("The scheme covers notified crops within notified insurance units (Gram Panchayat or Hobli):<br/>"
                           "• <b>Cereals & Millets:</b> Paddy / Rice (ಭತ್ತ), Ragi (ರಾಗಿ), Maize (ಮೆಕ್ಕೆಜೋಳ), Jowar / Sorghum (ಜೋಳ), Wheat (ಗೋಧಿ).<br/>"
                           "• <b>Pulses:</b> Red Gram / Tur (ತೊಗರಿ), Bengal Gram / Chickpea (ಕಡಲೆ), Green Gram (ಹೆಸರು), Black Gram (ಉದ್ದು).<br/>"
                           "• <b>Oilseeds:</b> Groundnut / Peanut (ಕಡಲೆಕಾಯಿ / ಶೇಂಗಾ), Soybean (ಸೋಯಾಬೀನ್), Sunflower (ಸೂರ್ಯಕಾಂತಿ), Sesamum (ಎಳ್ಳು).<br/>"
                           "• <b>Commercial & Horticultural:</b> Cotton (ಹತ್ತಿ), Sugarcane (ಕಬ್ಬು), Onion (ಈರುಳ್ಳಿ), Potato (ಆಲೂಗಡ್ಡೆ), Red Chilli (ಮೆಣಸಿನಕಾಯಿ).", s["body"]))
    story.append(Paragraph("ಕರ್ನಾಟಕದ ವಿವಿಧ ಜಿಲ್ಲೆಗಳಲ್ಲಿ ಅಧಿಸೂಚಿತವಾದ ಭತ್ತ, ರಾಗಿ, ಜೋಳ, ಮೆಕ್ಕೆಜೋಳ, ತೊಗರಿ, ಕಡಲೆ, ಶೇಂಗಾ, ಹತ್ತಿ, ಸೋಯಾಬೀನ್, ಕಬ್ಬು ಮೊದಲಾದ ಪ್ರಮುಖ ಬೆಳೆಗಳಿಗೆ ಗ್ರಾಮ ಪಂಚಾಯತ್ ಮಟ್ಟದಲ್ಲಿ ವಿಮೆ ಅನ್ವಯಿಸುತ್ತದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Beneficiary Eligibility & Tenant Cultivator Guidelines / ಅರ್ಹತೆ</b>", s["heading"]))
    story.append(Paragraph("• <b>Loanee Farmers:</b> All farmers who have availed Seasonal Agricultural Operational (SAO) loans or KCC crop credit for notified crops are covered automatically (with option to opt-out 7 days prior to cut-off).<br/>"
                           "• <b>Non-Loanee Farmers:</b> Eligible to enroll voluntarily through banks, RSKs, or Samrakshane portal.<br/>"
                           "• <b>Tenant Farmers & Sharecroppers:</b> Fully eligible to enroll by submitting a land lease agreement, tenancy declaration, or cultivation certificate issued by the Village Accountant or Gram Panchayat Nodal Officer along with the land RTC.", s["body"]))
    story.append(Paragraph("ಸ್ವಂತ ಜಮೀನು ಹೊಂದಿರುವ ರೈತರು ಮಾತ್ರವಲ್ಲದೆ, ಗೇಣಿದಾರರು (Tenant Farmers) ಮತ್ತು ಪಾಲುದಾರ ರೈತರು ಸಹ ಗ್ರಾಮ ಲೆಕ್ಕಿಗರು ನೀಡಿದ ಸಾಗುವಳಿ ಪ್ರಮಾಣಪತ್ರದೊಂದಿಗೆ ಬೆಳೆ ವಿಮೆ ಮಾಡಿಸಲು ಸಂಪೂರ್ಣ ಅರ್ಹರಾಗಿದ್ದಾರೆ.", s["kn"]))

    story.append(PageBreak())

    # PAGE 3
    story.append(Paragraph("GOVERNMENT OF KARNATAKA - SAMRAKSHANE PORTAL | CLAIMS & 72-HOUR TIMELINE", s["tag"]))
    story.append(Paragraph("<b>PMFBY Karnataka - 72-Hour Calamity Intimation & Claim Settlement</b>", s["title"]))
    story.append(Paragraph("ಬೆಳೆ ನಷ್ಟ ಪರಿಹಾರ - ೭೨ ಗಂಟೆಗಳ ಕಡ್ಡಾಯ ವರದಿ ನಿಯಮ ಮತ್ತು ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c62828"), spaceAfter=10))

    story.append(Paragraph("<b>1. STRICT 72-HOUR CALAMITY INTIMATION RULE / ೭೨ ಗಂಟೆಗಳ ಕಡ್ಡಾಯ ವರದಿ ನಿಯಮ</b>", s["heading"]))
    story.append(Paragraph("For individual farm-level localized calamities such as <b>Hailstorm, Landslide, Inundation, Cloudburst, or Natural Fire</b>, and for <b>Post-Harvest losses</b> (damage to harvested crop left in the field up to 14 days for drying due to unseasonal rains):<br/>"
                           "<b>THE AFFECTED FARMER MUST INTIMATE THE LOSS WITHIN 72 HOURS (3 CALENDAR DAYS)</b> from the time of the event! Intimations submitted after 72 hours are subject to immediate rejection under insurance regulatory norms.", s["body"]))
    story.append(Paragraph("ಗಮನಿಸಿ: ಆಲಿಕಲ್ಲು ಮಳೆ, ಜಲಾವೃತ (ನೆರೆ), ಭೂಕುಸಿತ ಅಥವಾ ಅಕಾಲಿಕ ಮಳೆಯಿಂದ ಬೆಳೆ ನಷ್ಟವಾದರೆ ರೈತರು ಕಡ್ಡಾಯವಾಗಿ <b>೭೨ ಗಂಟೆಗಳ ಒಳಗೆ (ಮೂರು ದಿನಗಳ ಒಳಗಾಗಿ)</b> ಮಾಹಿತಿ ನೀಡಬೇಕು. ತಡವಾದರೆ ವಿಮಾ ಕಂಪನಿ ಕ್ಲೈಮ್ ತಿರಸ್ಕರಿಸಬಹುದು.", s["kn"]))

    story.append(Paragraph("<b>2. How to Report Calamities in Karnataka / ನಷ್ಟ ವರದಿ ಮಾಡುವ ವಿಧಾನ</b>", s["heading"]))
    story.append(Paragraph("• <b>Samrakshane Portal:</b> Visit samrakshane.karnataka.gov.in and report under 'Crop Loss Intimation'.<br/>"
                           "• <b>Crop Insurance Mobile App:</b> Report with geotagged photo on the central PMFBY App.<br/>"
                           "• <b>Toll-free Hotline:</b> Dial Karnataka Samrakshane Helpline <b>1800-180-1551</b> or Kisan Call Centre <b>1800-180-1551</b>.<br/>"
                           "• <b>In-person:</b> Written notice to local Raitha Samparka Kendra (RSK) Agricultural Officer or bank branch.", s["body"]))

    story.append(Paragraph("<b>3. Assessment & Direct Benefit Settlement / ಪರಿಹಾರ ಪಾವತಿ</b>", s["heading"]))
    story.append(Paragraph("A joint inspection committee comprising the taluk Agriculture Officer, Revenue Inspector, and Insurance surveyor conducts field loss assessment within 10 days of intimation. For widespread yield loss, claims are determined based on Crop Cutting Experiments (CCE) conducted at Gram Panchayat level. Approved compensation is directly credited via DBT to the farmer's bank account.", s["body"]))

    doc.build(story)
    print("Generated:", pdf_path)

def create_krishi_bhagya_pdf():
    pdf_path = os.path.join(OUT_DIR, "Karnataka_Krishi_Bhagya_Scheme_Dryland_Manual.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    s = get_styles()
    story = []

    # PAGE 1
    story.append(Paragraph("GOVERNMENT OF KARNATAKA - DEPARTMENT OF AGRICULTURE", s["tag"]))
    story.append(Paragraph("<b>Karnataka State Krishi Bhagya Scheme - Dryland Agriculture Manual</b>", s["title"]))
    story.append(Paragraph("ಕರ್ನಾಟಕ ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ - ಮಳೆಯಾಶ್ರಿತ ಪ್ರದೇಶಗಳ ರೈತರ ಸಮಗ್ರ ಕೈಪಿಡಿ", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Scheme Purpose & Rainfed Focus / ಯೋಜನೆಯ ಉದ್ದೇಶ</b>", s["heading"]))
    story.append(Paragraph("The Karnataka Krishi Bhagya Scheme was formulated by the Government of Karnataka to transform rainfed and dryland agriculture into sustainable, climate-resilient farming systems. The scheme operates across <b>131 notified drought-prone and rainfed taluks</b> covering North Karnataka, Central Karnataka, and Southern dry zones (including Belagavi, Bagalkote, Vijayapura, Dharwad, Gadag, Koppal, Raichur, Kalaburagi, Yadgir, Chitradurga, Tumakuru, Kolar, and Chikkaballapura).", s["body"]))
    story.append(Paragraph("ಕರ್ನಾಟಕದ ೧೩೧ ಮಳೆಯಾಶ್ರಿತ ಮತ್ತು ಬರಪೀಡಿತ ತಾಲೂಕುಗಳಲ್ಲಿ ಮಳೆಯ ನೀರನ್ನು ಸಂರಕ್ಷಿಸಿ, ಬೆಳೆಗಳಿಗೆ ರಕ್ಷಣಾತ್ಮಕ ನೀರಾವರಿ ಒದಗಿಸಲು ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆಯನ್ನು ಜಾರಿಗೊಳಿಸಲಾಗಿದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Key Infrastructure Components / ಪ್ರಮುಖ ಸೌಲಭ್ಯಗಳು</b>", s["heading"]))
    story.append(Paragraph("The Krishi Bhagya package consists of integrated water harvesting and conservation components:<br/>"
                           "1. <b>Farm Pond (ಕೃಷಿ ಹೊಂಡ / Krishi Honda):</b> Excavation of in-situ rainwater storage pond.<br/>"
                           "2. <b>Polythene / Tarpaulin Bed Lining (ಪಾಲಿಥಿನ್ ಹೊದಿಕೆ):</b> 500-micron UV-stabilized geomembrane to prevent water seepage into soil.<br/>"
                           "3. <b>Pump Set:</b> Diesel engine or Solar pump to draw stored water from the pond.<br/>"
                           "4. <b>Micro-Irrigation Equipment:</b> Drip irrigation or Sprinkler units for water-saving protective watering.<br/>"
                           "5. <b>Shade Net / Polyhouse:</b> Specialized structures for high-value vegetable and floral crops.", s["body"]))
    story.append(Paragraph("ಘಟಕಗಳು: 1. ಕೃಷಿ ಹೊಂಡ ನಿರ್ಮಾಣ, 2. ನೀರು ಇಂಗಿ ಹೋಗದಂತೆ ತಡೆಯಲು ಪಾಲಿಥಿನ್ ಹೊದಿಕೆ, 3. ಡೀಸೆಲ್/ಸೌರ ಪಂಪ್‌ಸೆಟ್, 4. ಹನಿ ಅಥವಾ ತುಂತುರು ನೀರಾವರಿ ಪರಿಕರಗಳು, 5. ನೆರಳು ಪರದೆ/ಹಸಿರು ಮನೆ.", s["kn"]))

    story.append(PageBreak())

    # PAGE 2
    story.append(Paragraph("GOVERNMENT OF KARNATAKA - KRISHI BHAGYA | SUBSIDY RATES & COSTS", s["tag"]))
    story.append(Paragraph("<b>Krishi Bhagya - Subsidy Rates, Unit Costs & Farm Pond Sizing</b>", s["title"]))
    story.append(Paragraph("ಕೃಷಿ ಭಾಗ್ಯ - ಸಹಾಯಧನ ದರಗಳು, ಘಟಕ ವೆಚ್ಚ ಮತ್ತು ಕೃಷಿ ಹೊಂಡದ ಅಳತೆಗಳು", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d47a1"), spaceAfter=10))

    story.append(Paragraph("<b>1. Government Subsidy Scale / ಸರ್ಕಾರಿ ಸಹಾಯಧನದ ವಿವರ</b>", s["heading"]))
    story.append(Paragraph("• <b>General Category Dryland Farmers:</b> Entitled to <b>80% government subsidy</b> on the total package cost. The beneficiary farmer contributes the balance 20%.<br/>"
                           "• <b>SC / ST Small & Marginal Farmers:</b> Entitled to <b>90% government subsidy</b> on the package cost. The farmer contributes only 10%.<br/>"
                           "• <b>Total Assistance Value:</b> Subsidies range from <b>Rs 1,25,000 up to Rs 1,75,000</b> per complete farm pond, lining, and pump package depending on dimension.", s["body"]))
    story.append(Paragraph("ಸಹಾಯಧನ: ಸಾಮಾನ್ಯ ವರ್ಗದ ರೈತರಿಗೆ <b>೮೦% (80%)</b> ಸಹಾಯಧನ ಹಾಗೂ ಪರಿಶಿಷ್ಟ ಜಾತಿ (SC) ಮತ್ತು ಪರಿಶಿಷ್ಟ ಪಂಗಡದ (ST) ರೈತರಿಗೆ <b>೯೦% (90%)</b> ಭಾರಿ ಸಹಾಯಧನ ದೊರೆಯುತ್ತದೆ. ಒಟ್ಟು ₹1,75,000 ವರೆಗೆ ಆರ್ಥಿಕ ನೆರವು ಸಿಗುತ್ತದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Standard Farm Pond Dimensions / ಕೃಷಿ ಹೊಂಡದ ಅಳತೆಗಳು</b>", s["heading"]))
    story.append(Paragraph("Depending on land size and water catchment, three standard dimensions are approved:<br/>"
                           "• <b>Type 1:</b> 10m x 10m x 3m depth (Water capacity approx 250 cubic meters / 2.50 Lakh Litres).<br/>"
                           "• <b>Type 2:</b> 15m x 15m x 3m depth (Water capacity approx 500 cubic meters / 5.00 Lakh Litres).<br/>"
                           "• <b>Type 3:</b> 21m x 21m x 3m depth (Water capacity approx 1000 cubic meters / 10.00 Lakh Litres).<br/>"
                           "Farm ponds must include protective chain-link fencing or barbed wire safety boundary to prevent accidental falls.", s["body"]))

    story.append(PageBreak())

    # PAGE 3
    story.append(Paragraph("GOVERNMENT OF KARNATAKA - KRISHI BHAGYA | ELIGIBILITY & HOW TO APPLY", s["tag"]))
    story.append(Paragraph("<b>Krishi Bhagya - Beneficiary Eligibility & Application Process</b>", s["title"]))
    story.append(Paragraph("ಕೃಷಿ ಭಾಗ್ಯ - ಫಲಾನುಭವಿಗಳ ಅರ್ಹತಾ ನಿಯಮಗಳು ಮತ್ತು ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಹಂತಗಳು", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Detailed Eligibility Criteria / ರೈತರ ಅರ್ಹತೆ</b>", s["heading"]))
    story.append(Paragraph("1. Farmer must be a cultivator of dryland / rainfed agricultural land situated in the 131 notified taluks.<br/>"
                           "2. Landholding: Minimum 1.0 acre of rainfed agricultural land. Priority is given to small and marginal farmers owning between 1.0 to 5.0 acres.<br/>"
                           "3. Farmer must hold clear registered land ownership recorded in Karnataka Bhoomi RTC (Pahani).<br/>"
                           "4. The applicant must not have availed farm pond assistance from any other government scheme (such as MGNREGA or Watershed Development) in the previous 5 years.", s["body"]))
    story.append(Paragraph("ಅರ್ಹತೆ: 1. ಮಳೆಯಾಶ್ರಿತ ಪ್ರದೇಶದ ಕೃಷಿಕರಾಗಿರಬೇಕು, 2. ಕನಿಷ್ಠ ೧ ಎಕರೆ ಜಮೀನು ಇರಬೇಕು (೫ ಎಕರೆ ಒಳಗಿನ ಸಣ್ಣ ರೈತರಿಗೆ ಮೊದಲ ಆದ್ಯತೆ), 3. ಸ್ವಂತ ಪಹಣಿ (RTC) ಇರಬೇಕು, 4. ಕಳೆದ ೫ ವರ್ಷಗಳಲ್ಲಿ ಕೃಷಿ ಹೊಂಡದ ಸವಲತ್ತು ಪಡೆದಿರಬಾರದು.", s["kn"]))

    story.append(Paragraph("<b>2. Application Procedure & Documents / ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ವಿಧಾನ</b>", s["heading"]))
    story.append(Paragraph("• <b>Where to Submit:</b> Farmers must submit applications to the local <b>Raitha Samparka Kendra (RSK)</b> or the Office of the Assistant Director of Agriculture (ADA) in their respective taluk.<br/>"
                           "• <b>Documents Required:</b> 1. Aadhaar Card, 2. Latest RTC / Pahani with survey number, 3. Caste Certificate from Tahsildar (for SC/ST 90% subsidy), 4. Bank Passbook copy with IFSC, 5. Passport photograph.<br/>"
                           "• <b>Verification Workflow:</b> The Agricultural Officer conducts a field pre-inspection to verify soil slope and catchment suitability. Following work order issuance and pond construction, geotagged photographs are uploaded to the portal, and the subsidy is released directly.", s["body"]))
    story.append(Paragraph("ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಸ್ಥಳೀಯ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ (RSK) ಅಥವಾ ತಾಲೂಕು ಸಹಾಯಕ ಕೃಷಿ ನಿರ್ದೇಶಕರ ಕಚೇರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ. ಪಹಣಿ, ಆಧಾರ್ ಮತ್ತು ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ ಸಲ್ಲಿಸಬೇಕು.", s["kn"]))

    doc.build(story)
    print("Generated:", pdf_path)

def create_kcc_pdf():
    pdf_path = os.path.join(OUT_DIR, "Kisan_Credit_Card_KCC_Crop_Loans_Handbook.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=35, bottomMargin=35)
    s = get_styles()
    story = []

    # PAGE 1
    story.append(Paragraph("RESERVE BANK OF INDIA & NABARD - AGRICULTURAL CREDIT GUIDELINES", s["tag"]))
    story.append(Paragraph("<b>Kisan Credit Card (KCC) Scheme Guidelines & Interest Subvention</b>", s["title"]))
    story.append(Paragraph("ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (ಕೆಸಿಸಿ) ಸಾಲ ಯೋಜನೆ ಮತ್ತು ಬಡ್ಡಿ ರಿಯಾಯಿತಿ ಕೈಪಿಡಿ", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Scheme Objective & Purpose / ಕೆಸಿಸಿ ಯೋಜನೆಯ ಉದ್ದೇಶ</b>", s["heading"]))
    story.append(Paragraph("The Kisan Credit Card (KCC) scheme was designed by RBI and NABARD to provide adequate, timely, and cost-effective credit from the formal banking sector to farmers. Credit is sanctioned for: cultivation of notified crops, post-harvest expenses, produce marketing loan, household consumption needs of farmer family, and working capital for maintenance of farm assets and allied activities (dairy, poultry, fisheries).", s["body"]))
    story.append(Paragraph("ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಯೋಜನೆಯು ರೈತರಿಗೆ ಸಕಾಲದಲ್ಲಿ, ಸುಲಭವಾಗಿ ಮತ್ತು ಕಡಿಮೆ ಬಡ್ಡಿದರದಲ್ಲಿ ಕೃಷಿ ಚಟುವಟಿಕೆಗಳಿಗೆ ಅಲ್ಪಾವಧಿ ಸಾಲ ಒದಗಿಸುವ ಮಹತ್ವದ ಯೋಜನೆಯಾಗಿದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Credit Limit & Collateral Security Norms / ಸಾಲದ ಮಿತಿ ಮತ್ತು ಭದ್ರತೆ</b>", s["heading"]))
    story.append(Paragraph("• <b>Credit Limit:</b> Determined based on the Scale of Finance (SOF) fixed by the District Level Technical Committee (DLTC) multiplied by cultivated acres, plus 10% for post-harvest/household expenses and 20% for farm asset repairs.<br/>"
                           "• <b>Subsidized Credit Ceiling:</b> Short-term crop loans up to <b>Rs 3.00 Lakh</b> are covered under the Central Modified Interest Subvention Scheme.<br/>"
                           "• <b>Collateral-Free Limit:</b> In accordance with RBI guidelines, agricultural crop loans up to <b>Rs 1.60 Lakh</b> are sanctioned <b>100% COLLATERAL-FREE</b> without any mortgage of land or third-party guarantee.<br/>"
                           "• <b>Validity:</b> KCC credit limit is sanctioned for 5 years with simple annual renewal.", s["body"]))
    story.append(Paragraph("ಸಾಲದ ಮಿತಿ: ₹3 ಲಕ್ಷದವರೆಗೆ ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರದ ಬೆಳೆ ಸಾಲ ಲಭ್ಯವಿದೆ. ₹1.60 ಲಕ್ಷದವರೆಗೆ ಯಾವುದೇ ಜಮೀನಿನ ಅಡಮಾನವಿಲ್ಲದೆ (Collateral-free) ಸಾಲ ನೀಡಲಾಗುತ್ತದೆ.", s["kn"]))

    story.append(PageBreak())

    # PAGE 2
    story.append(Paragraph("RBI & GOI - MODIFIED INTEREST SUBVENTION SCHEME (MISS)", s["tag"]))
    story.append(Paragraph("<b>KCC - Subsidized Interest Rates & Prompt Repayment Incentive</b>", s["title"]))
    story.append(Paragraph("ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ - ೪% ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರ ಮತ್ತು ಮರುಪಾವತಿ ಸವಲತ್ತು", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0d47a1"), spaceAfter=10))

    story.append(Paragraph("<b>1. Interest Rate Structure / ಬಡ್ಡಿದರದ ಲೆಕ್ಕಾಚಾರ</b>", s["heading"]))
    story.append(Paragraph("The interest subvention mechanism functions as follows for short-term crop loans up to Rs 3 Lakh:<br/>"
                           "1. Standard Benchmark Bank Lending Rate: 9.0% per annum.<br/>"
                           "2. Government of India Interest Subvention: 2.0% per annum credited directly to lending banks.<br/>"
                           "3. Normal Rate Charged to Farmer: 7.0% per annum.<br/>"
                           "4. <b>Prompt Repayment Incentive (PRI):</b> An additional <b>3.0% interest subvention</b> is awarded to farmers who repay their loan on or before the due date.<br/>"
                           "5. <b>Effective Interest Rate: ONLY 4.0% per annum</b> for prompt-repaying farmers!", s["body"]))
    story.append(Paragraph("ಬಡ್ಡಿದರದ ವಿವರ: ಸಾಲವನ್ನು ನಿಗದಿತ ದಿನಾಂಕದೊಳಗೆ ಮರುಪಾವತಿ ಮಾಡುವ ರೈತರಿಗೆ ಕೇವಲ <b>೪% (4%)</b> ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರ ಅನ್ವಯಿಸುತ್ತದೆ. ಕೇಂದ್ರ ಸರ್ಕಾರವು ಶೇ. ೩% ಪ್ರೋತ್ಸಾಹಕ ರಿಯಾಯಿತಿ ನೀಡುತ್ತದೆ.", s["kn"]))

    story.append(Paragraph("<b>2. Karnataka State Zero-Percent Interest Crop Loan / ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಶೂನ್ಯ ಬಡ್ಡಿ ಸಾಲ</b>", s["heading"]))
    story.append(Paragraph("In Karnataka, short-term crop loans up to <b>Rs 3.00 Lakh</b> disbursed through Primary Agricultural Credit Co-operative Societies (PACS) and District Central Co-operative (DCC) Banks carry <b>0% ZERO PERCENT INTEREST</b>. The Karnataka State Government absorbs the entire remaining 4% interest as state subsidy for farmers who repay within one year.", s["body"]))
    story.append(Paragraph("ಕರ್ನಾಟಕ ಸಹಕಾರಿ ಬ್ಯಾಂಕ್ (PACS/DCC) ಗಳ ಮೂಲಕ ಪಡೆಯುವ ₹3 ಲಕ್ಷದವರೆಗಿನ ಅಲ್ಪಾವಧಿ ಬೆಳೆ ಸಾಲಕ್ಕೆ ರೈತರಿಗೆ <b>ಶೂನ್ಯ (0%) ಬಡ್ಡಿದರ</b> ಇರುತ್ತದೆ. ನಿಗದಿತ ಸಮಯದಲ್ಲಿ ಮರುಪಾವತಿ ಮಾಡಿದರೆ ಸಂಪೂರ್ಣ ಬಡ್ಡಿಯನ್ನು ಕರ್ನಾಟಕ ಸರ್ಕಾರವೇ ಭರಿಸುತ್ತದೆ.", s["kn"]))

    story.append(PageBreak())

    # PAGE 3
    story.append(Paragraph("NABARD & COMMERCIAL BANKS | KCC APPLICATION & DOCUMENTATION", s["tag"]))
    story.append(Paragraph("<b>KCC - Beneficiary Eligibility, Required Documents & Banks</b>", s["title"]))
    story.append(Paragraph("ಕೆಸಿಸಿ - ಫಲಾನುಭವಿಗಳ ಅರ್ಹತೆ, ಅಗತ್ಯ ದಾಖಲೆಗಳು ಮತ್ತು ಬ್ಯಾಂಕ್ ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆ", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1b5e20"), spaceAfter=10))

    story.append(Paragraph("<b>1. Eligible Beneficiaries / ಯಾರು ಅರ್ಜಿ ಸಲ್ಲಿಸಬಹುದು?</b>", s["heading"]))
    story.append(Paragraph("• All individual land-owning farmers cultivating agricultural crops.<br/>"
                           "• Joint cultivators, tenant farmers, oral lessees, and sharecroppers.<br/>"
                           "• Self Help Groups (SHGs) and Joint Liability Groups (JLGs) of small and marginal farmers.<br/>"
                           "• Animal husbandry, dairy, and fisheries farmers (up to Rs 2.00 Lakh working capital credit at 4% prompt repayment).", s["body"]))
    story.append(Paragraph("ಸ್ವಂತ ಜಮೀನು ಹೊಂದಿರುವ ರೈತರು, ಗೇಣಿದಾರರು (Tenant Farmers), ಜಂಟಿ ಹೊಣೆಗಾರಿಕೆ ಗುಂಪುಗಳು (JLG) ಹಾಗೂ ಹೈನುಗಾರಿಕೆ ಮತ್ತು ಕುರಿ ಸಾಕಾಣಿಕೆ ಮಾಡುವ ರೈತರು ಅರ್ಹರು.", s["kn"]))

    story.append(Paragraph("<b>2. Mandatory Documents for KCC / ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು</b>", s["heading"]))
    story.append(Paragraph("1. Duly completed KCC Application Form.<br/>"
                           "2. Two passport size photographs.<br/>"
                           "3. Proof of Identity: Aadhaar Card, Voter ID, or PAN Card.<br/>"
                           "4. Proof of Address: Aadhaar Card or Ration Card.<br/>"
                           "5. Land Records: Latest Karnataka Bhoomi RTC / Pahani showing crops grown and survey numbers.<br/>"
                           "6. No-dues certificate or self-declaration of no prior defaulted loans.", s["body"]))

    story.append(Paragraph("<b>3. Where to Apply & Processing Timelines / ಎಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು?</b>", s["heading"]))
    story.append(Paragraph("Farmers can submit applications at: 1. Public Sector Commercial Banks (State Bank of India, Canara Bank, Bank of Baroda), 2. Karnataka Gramin Bank (RRB), or 3. Local Primary Agricultural Credit Co-operative Societies (PACS). As per RBI mandates, commercial banks must sanction and issue KCC within <b>14 working days</b> of receipt of complete documents.", s["body"]))

    doc.build(story)
    print("Generated:", pdf_path)

if __name__ == "__main__":
    create_pm_kisan_pdf()
    create_pmfby_pdf()
    create_krishi_bhagya_pdf()
    create_kcc_pdf()
    print("All 4 official scheme PDF documents created successfully in scheme_documents!")


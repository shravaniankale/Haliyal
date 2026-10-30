from fastapi import APIRouter
from ..seed_data import AGRICULTURAL_LOANS
from ..schemas import LoanCalcRequest, LoanCalcResponse

router = APIRouter(prefix="/api/loans", tags=["Agriculture Loans"])

@router.get("")
def get_all_loans():
    """Returns verified agricultural credit and loan options for Karnataka farmers."""
    return AGRICULTURAL_LOANS

@router.post("/calculator", response_model=LoanCalcResponse)
def calculate_loan_emi(data: LoanCalcRequest):
    """
    Computes exact mathematical monthly EMI, total interest, and total repayment.
    Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    """
    principal = data.amount
    annual_rate = data.interest_rate
    months = data.tenure_months

    if months <= 0 or principal <= 0:
        return LoanCalcResponse(
            monthly_emi=0.0,
            total_interest=0.0,
            total_payment=principal,
            principal=principal
        )

    monthly_rate = (annual_rate / 100.0) / 12.0

    if monthly_rate == 0:
        emi = principal / months
        total_payment = principal
        total_interest = 0.0
    else:
        factor = (1.0 + monthly_rate) ** months
        emi = principal * monthly_rate * factor / (factor - 1.0)
        total_payment = emi * months
        total_interest = total_payment - principal

    return LoanCalcResponse(
        monthly_emi=round(emi, 2),
        total_interest=round(total_interest, 2),
        total_payment=round(total_payment, 2),
        principal=round(principal, 2)
    )

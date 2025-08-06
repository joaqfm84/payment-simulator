from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import uuid
import json
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import threading
import time

app = Flask(__name__)
CORS(app)

# In-memory storage for transfers and bank accounts
transfers = {}
bank_accounts = {}

class BankAccount:
    def __init__(self, account_number, institution_number, transit_number, account_holder, currency="CAD", initial_balance=10000.00):
        self.account_number = account_number
        self.institution_number = institution_number
        self.transit_number = transit_number
        self.account_holder = account_holder
        self.currency = currency
        self.balance = initial_balance
        self.transactions = []
        self.account_id = f"{institution_number}-{transit_number}-{account_number}"
    
    def debit(self, amount, description, transfer_id):
        if self.balance >= amount:
            self.balance -= amount
            self.transactions.append({
                "timestamp": datetime.now().isoformat(),
                "type": "DEBIT",
                "amount": amount,
                "description": description,
                "transfer_id": transfer_id,
                "balance_after": self.balance
            })
            return True
        return False
    
    def credit(self, amount, description, transfer_id):
        self.balance += amount
        self.transactions.append({
            "timestamp": datetime.now().isoformat(),
            "type": "CREDIT",
            "amount": amount,
            "description": description,
            "transfer_id": transfer_id,
            "balance_after": self.balance
        })
    
    def to_dict(self):
        return {
            "account_id": self.account_id,
            "account_holder": self.account_holder,
            "balance": self.balance,
            "currency": self.currency,
            "transactions": self.transactions
        }

class WireTransfer:
    def __init__(self, debtor_name, institution_number, transit_number, account_number,
                 creditor_name, creditor_iban, creditor_bic, amount, currency, purpose):
        self.id = str(uuid.uuid4())
        self.debtor_name = debtor_name
        self.institution_number = institution_number
        self.transit_number = transit_number
        self.account_number = account_number
        self.creditor_name = creditor_name
        self.creditor_iban = creditor_iban
        self.creditor_bic = creditor_bic
        self.amount = amount
        self.currency = currency
        self.purpose = purpose
        self.created_at = datetime.now().isoformat()
        self.status = "PENDING"
        self.pacs_008_xml = self.generate_pacs_008()
        self.pacs_002_xml = None
        self.pacs_004_xml = None
        self.pacs_007_xml = None
        self.processing_steps = []
        self.bank_accounts_affected = []
        
        # Initialize or get bank accounts
        self.initialize_bank_accounts()
        
        self.add_processing_step("Transfer initiated", "PENDING", 
                               f"Customer initiated wire transfer of {self.amount} {self.currency} from {self.debtor_name} to {self.creditor_name}")
        
        # Start the clearing and settlement simulation
        self.start_clearing_simulation()

    def initialize_bank_accounts(self):
        """Initialize or get existing bank accounts for the transfer"""
        # Debtor account
        debtor_account_id = f"{self.institution_number}-{self.transit_number}-{self.account_number}"
        if debtor_account_id not in bank_accounts:
            bank_accounts[debtor_account_id] = BankAccount(
                self.account_number, 
                self.institution_number, 
                self.transit_number, 
                self.debtor_name,
                self.currency
            )
        
        # Creditor account (simulated)
        creditor_account_id = f"CREDITOR-{self.creditor_iban[-8:]}"
        if creditor_account_id not in bank_accounts:
            bank_accounts[creditor_account_id] = BankAccount(
                self.creditor_iban[-8:],
                "999",  # Simulated institution
                "99999",  # Simulated transit
                self.creditor_name,
                self.currency
            )
        
        self.debtor_account = bank_accounts[debtor_account_id]
        self.creditor_account = bank_accounts[creditor_account_id]
        self.bank_accounts_affected = [debtor_account_id, creditor_account_id]

    def add_processing_step(self, step_name, status, details=""):
        """Add a processing step to the transfer"""
        step = {
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "status": status,
            "details": details
        }
        self.processing_steps.append(step)
        self.status = status

    def generate_pacs_002(self):
        """Generate ISO 20022 PACS.002 (Payment Status Report) message"""
        root = ET.Element("Document", {
            "xmlns": "urn:iso:std:iso:20022:tech:xsd:pacs.002.001.12",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        
        fitofi = ET.SubElement(root, "FIToFIPmtStsRpt")
        
        # Group Header
        grphdr = ET.SubElement(fitofi, "GrpHdr")
        msg_id = ET.SubElement(grphdr, "MsgId")
        msg_id.text = f"LYNX002{datetime.now().strftime('%Y%m%d%H%M%S')}{self.id[:8].upper()}"
        cre_dt_tm = ET.SubElement(grphdr, "CreDtTm")
        cre_dt_tm.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Original Group Information
        orgnl_grp_inf = ET.SubElement(fitofi, "OrgnlGrpInf")
        orgnl_msg_id = ET.SubElement(orgnl_grp_inf, "OrgnlMsgId")
        orgnl_msg_id.text = f"LYNX{self.id[:16].upper()}"
        orgnl_msg_nm_id = ET.SubElement(orgnl_grp_inf, "OrgnlMsgNmId")
        orgnl_msg_nm_id.text = "pacs.008.001.10"
        
        # Transaction Information
        tx_inf = ET.SubElement(fitofi, "TxInf")
        orgnl_end_to_end_id = ET.SubElement(tx_inf, "OrgnlEndToEndId")
        orgnl_end_to_end_id.text = f"E2E{self.id[:16].upper()}"
        orgnl_tx_id = ET.SubElement(tx_inf, "OrgnlTxId")
        orgnl_tx_id.text = f"LYNX{self.id[:16].upper()}"
        
        # Transaction Status
        tx_sts = ET.SubElement(tx_inf, "TxSts")
        tx_sts.text = "ACSP"  # AcceptedSettlementCompleted
        
        # Status Reason Information
        sts_rsn_inf = ET.SubElement(tx_inf, "StsRsnInf")
        rsn = ET.SubElement(sts_rsn_inf, "Rsn")
        cd = ET.SubElement(rsn, "Cd")
        cd.text = "AC01"  # Accepted
        
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def generate_pacs_004(self):
        """Generate ISO 20022 PACS.004 (Payment Return) message (for failed transfers)"""
        root = ET.Element("Document", {
            "xmlns": "urn:iso:std:iso:20022:tech:xsd:pacs.004.001.10",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        
        fitofi = ET.SubElement(root, "FIToFIPmtRvsl")
        
        # Group Header
        grphdr = ET.SubElement(fitofi, "GrpHdr")
        msg_id = ET.SubElement(grphdr, "MsgId")
        msg_id.text = f"LYNX004{datetime.now().strftime('%Y%m%d%H%M%S')}{self.id[:8].upper()}"
        cre_dt_tm = ET.SubElement(grphdr, "CreDtTm")
        cre_dt_tm.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Original Group Information
        orgnl_grp_inf = ET.SubElement(fitofi, "OrgnlGrpInf")
        orgnl_msg_id = ET.SubElement(orgnl_grp_inf, "OrgnlMsgId")
        orgnl_msg_id.text = f"LYNX{self.id[:16].upper()}"
        orgnl_msg_nm_id = ET.SubElement(orgnl_grp_inf, "OrgnlMsgNmId")
        orgnl_msg_nm_id.text = "pacs.008.001.10"
        
        # Transaction Information
        tx_inf = ET.SubElement(fitofi, "TxInf")
        rvsl_id = ET.SubElement(tx_inf, "RvslId")
        rvsl_id.text = f"REV{self.id[:16].upper()}"
        orgnl_tx_id = ET.SubElement(tx_inf, "OrgnlTxId")
        orgnl_tx_id.text = f"LYNX{self.id[:16].upper()}"
        
        # Returned Interbank Settlement Amount
        rtrd_intr_bk_sttlm_amt = ET.SubElement(tx_inf, "RtrdIntrBkSttlmAmt")
        rtrd_intr_bk_sttlm_amt.set("Ccy", self.currency)
        rtrd_intr_bk_sttlm_amt.text = str(self.amount)
        
        # Return Reason
        rtr_rsn_inf = ET.SubElement(tx_inf, "RtrRsnInf")
        rsn = ET.SubElement(rtr_rsn_inf, "Rsn")
        cd = ET.SubElement(rsn, "Cd")
        cd.text = "AC01"  # Account closed
        
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def generate_pacs_007(self):
        """Generate ISO 20022 PACS.007 (Payment Cancellation Request) message"""
        root = ET.Element("Document", {
            "xmlns": "urn:iso:std:iso:20022:tech:xsd:pacs.007.001.10",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        
        fitofi = ET.SubElement(root, "FIToFIPmtCxlReq")
        
        # Group Header
        grphdr = ET.SubElement(fitofi, "GrpHdr")
        msg_id = ET.SubElement(grphdr, "MsgId")
        msg_id.text = f"LYNX007{datetime.now().strftime('%Y%m%d%H%M%S')}{self.id[:8].upper()}"
        cre_dt_tm = ET.SubElement(grphdr, "CreDtTm")
        cre_dt_tm.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Original Group Information
        orgnl_grp_inf = ET.SubElement(fitofi, "OrgnlGrpInf")
        orgnl_msg_id = ET.SubElement(orgnl_grp_inf, "OrgnlMsgId")
        orgnl_msg_id.text = f"LYNX{self.id[:16].upper()}"
        orgnl_msg_nm_id = ET.SubElement(orgnl_grp_inf, "OrgnlMsgNmId")
        orgnl_msg_nm_id.text = "pacs.008.001.10"
        
        # Transaction Information
        tx_inf = ET.SubElement(fitofi, "TxInf")
        cxl_id = ET.SubElement(tx_inf, "CxlId")
        cxl_id.text = f"CXL{self.id[:16].upper()}"
        orgnl_tx_id = ET.SubElement(tx_inf, "OrgnlTxId")
        orgnl_tx_id.text = f"LYNX{self.id[:16].upper()}"
        
        # Cancellation Reason
        cxl_rsn_inf = ET.SubElement(tx_inf, "CxlRsnInf")
        rsn = ET.SubElement(cxl_rsn_inf, "Rsn")
        cd = ET.SubElement(rsn, "Cd")
        cd.text = "CUST"  # Customer requested
        
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def start_clearing_simulation(self):
        """Simulate the clearing and settlement process"""
        def simulate_clearing():
            # Step 1: Message validation (2 seconds)
            time.sleep(2)
            validation_details = f"""🏦 **ORIGINATING BANK** validates the PACS.008 message format and required fields:

📋 **XML Schema Validation** (performed by bank's payment system):
• Namespace compliance: urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10
• XML structure validation against ISO 20022 schema
• Element hierarchy and nesting validation

🔍 **Required Fields Check** (validated by originating bank):
• GrpHdr/MsgId: LYNX{self.id[:8].upper()} ✓
• GrpHdr/CreDtTm: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")} ✓
• GrpHdr/NbOfTxs: 1 ✓
• GrpHdr/CtrlSum: {self.amount} ✓
• CdtTrfTxInf/PmtId/InstrId: LYNX{self.id[:16].upper()} ✓
• CdtTrfTxInf/PmtId/EndToEndId: E2E{self.id[:16].upper()} ✓
• CdtTrfTxInf/IntrBkSttlmAmt: {self.amount} {self.currency} ✓
• CdtTrfTxInf/Dbtr/Nm: {self.debtor_name} ✓
• CdtTrfTxInf/Cdtr/Nm: {self.creditor_name} ✓
• CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI: LYNXCA22XXX ✓
• CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI: {self.creditor_bic} ✓

✅ **Validation Result**: All required fields present and valid
📍 **Location**: Originating Bank's Payment Processing System"""
            
            self.add_processing_step("PACS.008 message validation", "VALIDATING", validation_details)
            
            # Step 2: Bank validation and fund reservation (3 seconds)
            time.sleep(3)
            if self.debtor_account.debit(self.amount, f"Wire transfer to {self.creditor_name}", self.id):
                self.add_processing_step("Bank account validation & fund reservation", "VALIDATING", 
                                       f"""🏦 **ORIGINATING BANK** validates the debtor account and reserves funds:

💰 **Account Validation** (performed by originating bank):
• Account verification: {self.institution_number}-{self.transit_number}-{self.account_number}
• Account status check: Active ✓
• Balance verification: {self.debtor_account.balance} {self.currency} available
• Transaction limits validation: Within daily limits ✓
• Canadian routing number validation: {self.institution_number} (valid institution code)

💳 **Fund Reservation** (performed by originating bank):
• Amount reserved: {self.amount} {self.currency}
• New available balance: {self.debtor_account.balance} {self.currency}
• Funds held for settlement (not yet transferred)

📍 **Location**: Originating Bank's Core Banking System""")
            else:
                self.add_processing_step("Bank account validation failed", "FAILED", 
                                       f"""❌ **ORIGINATING BANK** validation failed:

💰 **Insufficient Funds** (detected by originating bank):
• Account: {self.institution_number}-{self.transit_number}-{self.account_number}
• Required amount: {self.amount} {self.currency}
• Available balance: {self.debtor_account.balance} {self.currency}
• Shortfall: {self.amount - self.debtor_account.balance} {self.currency}

📍 **Location**: Originating Bank's Core Banking System
🚫 **Action**: Transfer rejected - no funds reserved""")
                return
            
            # Step 3: Message sent to clearing system (2 seconds)
            time.sleep(2)
            clearing_system = "Lynx" if self.currency == "CAD" else "SWIFT"
            self.add_processing_step("Message sent to Lynx/SWIFT", "PROCESSING", 
                                   f"""🏦 **ORIGINATING BANK** sends PACS.008 message to clearing system:

📤 **Message Transmission** (performed by originating bank):
• PACS.008 message sent to {clearing_system} clearing system
• Message routing through secure financial network
• End-to-end encryption applied

🌐 **Clearing System Selection**:
• {clearing_system} system selected for {self.currency} transfer
• {'Lynx (Payments Canada domestic system)' if self.currency == 'CAD' else 'SWIFT (international messaging network)'}

📍 **Location**: Originating Bank → {clearing_system} Network
🔐 **Security**: Encrypted financial messaging""")
            
            # Step 4: Clearing processing and interbank settlement (4 seconds)
            time.sleep(4)
            self.add_processing_step("Clearing and settlement", "SETTLING", 
                                   f"""🏛️ **{clearing_system.upper()} CLEARING SYSTEM** processes the interbank settlement:

💼 **Clearing Processing** (performed by {clearing_system}):
• Message received and validated by {clearing_system}
• Transaction amount: {self.amount} {self.currency}
• Real-time gross settlement (RTGS) processing

🏦 **Interbank Settlement** (performed by {clearing_system}):
• Originating bank: LYNXCA22XXX (debtor's bank)
• Receiving bank: {self.creditor_bic} (creditor's bank)
• Settlement finality achieved - transaction is irrevocable
• Funds moved between bank settlement accounts

📍 **Location**: {clearing_system} Clearing System
⚡ **Processing**: Real-time gross settlement (RTGS)""")
            
            # Step 5: Funds credited to beneficiary (2 seconds)
            time.sleep(2)
            self.creditor_account.credit(self.amount, f"Wire transfer from {self.debtor_name}", self.id)
            self.add_processing_step("Funds credited to beneficiary", "COMPLETED", 
                                   f"""🏦 **RECEIVING BANK** credits funds to the beneficiary account:

💰 **Fund Credit** (performed by receiving bank):
• Amount credited: {self.amount} {self.currency}
• Beneficiary: {self.creditor_name}
• Account: {self.creditor_iban}
• Bank: {self.creditor_bic}
• New balance: {self.creditor_account.balance} {self.currency}

✅ **Settlement Finality**:
• Transaction is irrevocable
• Funds are immediately available to beneficiary
• Settlement confirmation sent to originating bank

📍 **Location**: Receiving Bank's Core Banking System
📧 **Notification**: Beneficiary notified of credit""")
            
            # Step 6: Generate PACS.002 confirmation message (1 second)
            time.sleep(1)
            self.pacs_002_xml = self.generate_pacs_002()
            self.add_processing_step("PACS.002 confirmation sent", "COMPLETED", 
                                   f"""🏦 **RECEIVING BANK** sends PACS.002 confirmation to originating bank:

📤 **Confirmation Message** (sent by receiving bank):
• PACS.002 status report generated
• End-to-end reference: E2E{self.id[:16].upper()}
• Transaction status: ACSP (AcceptedSettlementCompleted)
• Confirmation sent to originating bank

📧 **Customer Notifications**:
• Originating bank notifies debtor of successful transfer
• Receiving bank notifies creditor of received funds
• Transaction traceability maintained throughout process

📍 **Location**: Receiving Bank → Originating Bank
✅ **Status**: Transfer completed successfully""")
        
        # Start the simulation in a separate thread
        thread = threading.Thread(target=simulate_clearing)
        thread.daemon = True
        thread.start()

    def generate_pacs_008(self):
        """Generate ISO 20022 PACS.008 XML message"""
        # Create the root element with proper namespaces
        root = ET.Element("Document", {
            "xmlns": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        
        # Create FIToFI Customer Credit Transfer
        fitofi = ET.SubElement(root, "FIToFICstmrCdtTrf")
        
        # Group Header
        grphdr = ET.SubElement(fitofi, "GrpHdr")
        msg_id = ET.SubElement(grphdr, "MsgId")
        msg_id.text = f"LYNX{datetime.now().strftime('%Y%m%d%H%M%S')}{self.id[:8].upper()}"
        cre_dt_tm = ET.SubElement(grphdr, "CreDtTm")
        cre_dt_tm.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        nb_of_txs = ET.SubElement(grphdr, "NbOfTxs")
        nb_of_txs.text = "1"
        ctrl_sum = ET.SubElement(grphdr, "CtrlSum")
        ctrl_sum.text = str(self.amount)
        
        # Initiating Party
        initg_pty = ET.SubElement(grphdr, "InitgPty")
        initg_pty_nm = ET.SubElement(initg_pty, "Nm")
        initg_pty_nm.text = self.debtor_name
        
        # Credit Transfer Transaction Information
        cdt_trf_tx_inf = ET.SubElement(fitofi, "CdtTrfTxInf")
        
        # Payment Identification
        pmt_id = ET.SubElement(cdt_trf_tx_inf, "PmtId")
        instr_id = ET.SubElement(pmt_id, "InstrId")
        instr_id.text = f"LYNX{self.id[:16].upper()}"
        end_to_end_id = ET.SubElement(pmt_id, "EndToEndId")
        end_to_end_id.text = f"E2E{self.id[:16].upper()}"
        
        # Interbank Settlement Amount
        intr_bk_sttlm_amt = ET.SubElement(cdt_trf_tx_inf, "IntrBkSttlmAmt")
        intr_bk_sttlm_amt.set("Ccy", self.currency)
        intr_bk_sttlm_amt.text = str(self.amount)
        
        # Charge Bearer
        chrg_br = ET.SubElement(cdt_trf_tx_inf, "ChrgBr")
        chrg_br.text = "DEBT"
        
        # Debtor
        dbtr = ET.SubElement(cdt_trf_tx_inf, "Dbtr")
        dbtr_nm = ET.SubElement(dbtr, "Nm")
        dbtr_nm.text = self.debtor_name
        
        # Debtor Account
        dbtr_acct = ET.SubElement(cdt_trf_tx_inf, "DbtrAcct")
        id_elem = ET.SubElement(dbtr_acct, "Id")
        othr = ET.SubElement(id_elem, "Othr")
        id_val = ET.SubElement(othr, "Id")
        id_val.text = f"{self.institution_number}{self.transit_number}{self.account_number}"
        
        # Debtor Agent (Canadian Bank)
        dbtr_agt = ET.SubElement(cdt_trf_tx_inf, "DbtrAgt")
        fin_instn_id = ET.SubElement(dbtr_agt, "FinInstnId")
        bicfi = ET.SubElement(fin_instn_id, "BICFI")
        bicfi.text = "LYNXCA22XXX"  # Lynx BIC
        
        # Creditor Agent
        cdtr_agt = ET.SubElement(cdt_trf_tx_inf, "CdtrAgt")
        fin_instn_id_cdtr = ET.SubElement(cdtr_agt, "FinInstnId")
        bicfi_cdtr = ET.SubElement(fin_instn_id_cdtr, "BICFI")
        bicfi_cdtr.text = self.creditor_bic
        
        # Creditor
        cdtr = ET.SubElement(cdt_trf_tx_inf, "Cdtr")
        cdtr_nm = ET.SubElement(cdtr, "Nm")
        cdtr_nm.text = self.creditor_name
        
        # Creditor Account
        cdtr_acct = ET.SubElement(cdt_trf_tx_inf, "CdtrAcct")
        id_elem_cdtr = ET.SubElement(cdtr_acct, "Id")
        iban = ET.SubElement(id_elem_cdtr, "IBAN")
        iban.text = self.creditor_iban
        
        # Purpose
        purp = ET.SubElement(cdt_trf_tx_inf, "Purp")
        cd = ET.SubElement(purp, "Cd")
        cd.text = "CASH"  # Default purpose code
        
        # Remittance Information
        rmt_inf = ET.SubElement(cdt_trf_tx_inf, "RmtInf")
        strd = ET.SubElement(rmt_inf, "Strd")
        rfrd_doc_inf = ET.SubElement(strd, "RfrdDocInf")
        nb = ET.SubElement(rfrd_doc_inf, "Nb")
        nb.text = "1"
        rltd_dt = ET.SubElement(rfrd_doc_inf, "RltdDt")
        rltd_dt.text = datetime.now().strftime("%Y-%m-%d")
        
        # Structured Remittance Information
        strd_rmt_inf = ET.SubElement(strd, "StrdRmtInf")
        rfrd_inv_amt = ET.SubElement(strd_rmt_inf, "RfrdInvAmt")
        rmtd_amt = ET.SubElement(rfrd_inv_amt, "RmtdAmt")
        rmtd_amt.set("Ccy", self.currency)
        rmtd_amt.text = str(self.amount)
        
        # Creditor Reference Information
        cdtr_ref_inf = ET.SubElement(strd_rmt_inf, "CdtrRefInf")
        tp = ET.SubElement(cdtr_ref_inf, "Tp")
        cd_tp = ET.SubElement(tp, "Cd")
        cd_tp.text = "SCOR"
        ref = ET.SubElement(cdtr_ref_inf, "Ref")
        ref.text = f"REF{self.id[:16].upper()}"
        
        # Pretty print the XML
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def to_dict(self):
        return {
            'id': self.id,
            'debtor_name': self.debtor_name,
            'institution_number': self.institution_number,
            'transit_number': self.transit_number,
            'account_number': self.account_number,
            'creditor_name': self.creditor_name,
            'creditor_iban': self.creditor_iban,
            'creditor_bic': self.creditor_bic,
            'amount': self.amount,
            'currency': self.currency,
            'purpose': self.purpose,
            'created_at': self.created_at,
            'status': self.status,
            'pacs_008_xml': self.pacs_008_xml,
            'pacs_002_xml': self.pacs_002_xml,
            'pacs_004_xml': self.pacs_004_xml,
            'pacs_007_xml': self.pacs_007_xml,
            'processing_steps': self.processing_steps,
            'bank_accounts_affected': self.bank_accounts_affected,
            'debtor_account': self.debtor_account.to_dict() if hasattr(self, 'debtor_account') else None,
            'creditor_account': self.creditor_account.to_dict() if hasattr(self, 'creditor_account') else None
        }

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/create_transfer', methods=['POST'])
def create_transfer():
    """Handle transfer creation and generate PACS.008 XML"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'debtor_name', 'institution_number', 'transit_number', 'account_number',
            'creditor_name', 'creditor_iban', 'creditor_bic', 'amount', 'currency', 'purpose'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create transfer
        transfer = WireTransfer(
            debtor_name=data['debtor_name'],
            institution_number=data['institution_number'],
            transit_number=data['transit_number'],
            account_number=data['account_number'],
            creditor_name=data['creditor_name'],
            creditor_iban=data['creditor_iban'],
            creditor_bic=data['creditor_bic'],
            amount=float(data['amount']),
            currency=data['currency'],
            purpose=data['purpose']
        )
        
        # Store transfer
        transfers[transfer.id] = transfer
        
        return jsonify({
            'message': 'Transfer created successfully',
            'transfer_id': transfer.id,
            'transfer': transfer.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transfers', methods=['GET'])
def list_transfers():
    """List all transfers"""
    transfer_list = [transfer.to_dict() for transfer in transfers.values()]
    return jsonify({
        'transfers': transfer_list,
        'count': len(transfer_list)
    })

@app.route('/transfer/<transfer_id>', methods=['GET'])
def get_transfer(transfer_id):
    """View transfer details"""
    if transfer_id not in transfers:
        return jsonify({'error': 'Transfer not found'}), 404
    
    return jsonify(transfers[transfer_id].to_dict())

@app.route('/bank_accounts', methods=['GET'])
def list_bank_accounts():
    """List all bank accounts"""
    account_list = [account.to_dict() for account in bank_accounts.values()]
    return jsonify({
        'bank_accounts': account_list,
        'count': len(account_list)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Wire Transfer Simulator API is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
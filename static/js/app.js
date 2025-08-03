const API_BASE_URL = 'http://localhost:5000';

function App() {
    const [transfers, setTransfers] = React.useState([]);
    const [loading, setLoading] = React.useState(false);
    const [selectedTransfer, setSelectedTransfer] = React.useState(null);
    const [activeTab, setActiveTab] = React.useState(0);
    const [showModal, setShowModal] = React.useState(false);

    React.useEffect(() => {
        fetchTransfers();
        // Set up real-time updates every 2 seconds
        const interval = setInterval(fetchTransfers, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchTransfers = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/transfers`);
            setTransfers(response.data.transfers);
        } catch (error) {
            console.error('Error fetching transfers:', error);
        }
    };

    const handleTransferSubmit = async (formData) => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/create_transfer`, formData);
            alert(`Transfer created successfully! Transfer ID: ${response.data.transfer_id}`);
            fetchTransfers();
            setActiveTab(1); // Switch to transfers tab
        } catch (error) {
            alert(`Error: ${error.response?.data?.error || "Failed to create transfer"}`);
        } finally {
            setLoading(false);
        }
    };

    const viewTransferDetails = async (transferId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/transfer/${transferId}`);
            setSelectedTransfer(response.data);
            setShowModal(true);
        } catch (error) {
            alert("Failed to fetch transfer details");
        }
    };

    return (
        <div className="container">
            <div className="header">
                <h1>🇨🇦 Canadian Wire Transfer Simulator</h1>
                <p>Simulate ISO 20022 PACS.008 messages for Lynx and SWIFT transfers</p>
            </div>

            <div className="tabs">
                <button 
                    className={`tab ${activeTab === 0 ? 'active' : ''}`}
                    onClick={() => setActiveTab(0)}
                >
                    Create Transfer
                </button>
                <button 
                    className={`tab ${activeTab === 1 ? 'active' : ''}`}
                    onClick={() => setActiveTab(1)}
                >
                    View Transfers
                </button>
                <button 
                    className={`tab ${activeTab === 2 ? 'active' : ''}`}
                    onClick={() => setActiveTab(2)}
                >
                    About
                </button>
            </div>

            <div className={`tab-content ${activeTab === 0 ? 'active' : ''}`}>
                <TransferForm onSubmit={handleTransferSubmit} loading={loading} />
            </div>
            
            <div className={`tab-content ${activeTab === 1 ? 'active' : ''}`}>
                <TransferList 
                    transfers={transfers} 
                    onViewDetails={viewTransferDetails}
                    onRefresh={fetchTransfers}
                />
            </div>
            
            <div className={`tab-content ${activeTab === 2 ? 'active' : ''}`}>
                <AboutSection />
            </div>

            <TransferDetailsModal 
                transfer={selectedTransfer} 
                isOpen={showModal} 
                onClose={() => setShowModal(false)} 
            />
        </div>
    );
}

function HelpIcon({ tooltip }) {
    return (
        <div className="help-icon">
            ?
            <div className="tooltip">{tooltip}</div>
        </div>
    );
}

function TransferForm({ onSubmit, loading }) {
    const [formData, setFormData] = React.useState({
        debtor_name: '',
        institution_number: '',
        transit_number: '',
        account_number: '',
        creditor_name: '',
        creditor_iban: 'DE89370400440532013000',
        creditor_bic: 'COBADEFFXXX',
        amount: '',
        currency: 'CAD',
        purpose: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    return (
        <div className="card">
            <div className="card-header">
                <h2>Create New Wire Transfer</h2>
            </div>
            <div className="card-body">
                <form onSubmit={handleSubmit}>
                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Debtor Name</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.debtor_name}
                                    onChange={(e) => handleChange('debtor_name', e.target.value)}
                                    placeholder="John Doe"
                                    required
                                />
                                <HelpIcon tooltip="The name of the person or company sending the money (payer)" />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Amount</label>
                            <div className="field-container">
                                <input 
                                    type="number"
                                    step="0.01"
                                    className="form-input form-input-with-help"
                                    value={formData.amount}
                                    onChange={(e) => handleChange('amount', e.target.value)}
                                    placeholder="1000.00"
                                    required
                                />
                                <HelpIcon tooltip="The amount of money to be transferred (e.g., 1000.00)" />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Currency</label>
                            <div className="field-container">
                                <select 
                                    className="form-select form-select-with-help"
                                    value={formData.currency}
                                    onChange={(e) => handleChange('currency', e.target.value)}
                                >
                                    <option value="CAD">CAD</option>
                                    <option value="USD">USD</option>
                                    <option value="EUR">EUR</option>
                                </select>
                                <HelpIcon tooltip="The currency of the transfer (CAD for Canadian Dollar, USD for US Dollar, EUR for Euro)" />
                            </div>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Institution Number</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.institution_number}
                                    onChange={(e) => handleChange('institution_number', e.target.value)}
                                    placeholder="003"
                                    required
                                />
                                <HelpIcon tooltip="3-digit code identifying the Canadian financial institution (e.g., 003 for Royal Bank)" />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Transit Number</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.transit_number}
                                    onChange={(e) => handleChange('transit_number', e.target.value)}
                                    placeholder="12345"
                                    required
                                />
                                <HelpIcon tooltip="5-digit code identifying the specific bank branch (e.g., 12345)" />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Account Number</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.account_number}
                                    onChange={(e) => handleChange('account_number', e.target.value)}
                                    placeholder="1234567890"
                                    required
                                />
                                <HelpIcon tooltip="The customer's account number at the Canadian bank (e.g., 1234567890)" />
                            </div>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Creditor Name</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.creditor_name}
                                    onChange={(e) => handleChange('creditor_name', e.target.value)}
                                    placeholder="Jane Smith"
                                    required
                                />
                                <HelpIcon tooltip="The name of the person or company receiving the money (payee)" />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Creditor IBAN</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.creditor_iban}
                                    onChange={(e) => handleChange('creditor_iban', e.target.value)}
                                    placeholder="DE89370400440532013000"
                                    required
                                />
                                <HelpIcon tooltip="International Bank Account Number for the recipient's account (e.g., DE89370400440532013000)" />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Creditor BIC</label>
                            <div className="field-container">
                                <input 
                                    type="text"
                                    className="form-input form-input-with-help"
                                    value={formData.creditor_bic}
                                    onChange={(e) => handleChange('creditor_bic', e.target.value)}
                                    placeholder="COBADEFFXXX"
                                    required
                                />
                                <HelpIcon tooltip="Bank Identifier Code (SWIFT code) for the recipient's bank (e.g., COBADEFFXXX)" />
                            </div>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Purpose</label>
                        <div className="field-container">
                            <textarea 
                                className="form-textarea form-textarea-with-help"
                                value={formData.purpose}
                                onChange={(e) => handleChange('purpose', e.target.value)}
                                placeholder="Payment for services"
                            />
                            <HelpIcon tooltip="Optional description of the payment purpose (e.g., 'Payment for services', 'Invoice payment')" />
                        </div>
                    </div>

                    <button 
                        type="submit" 
                        className={`btn btn-primary ${loading ? 'loading' : ''}`}
                        disabled={loading}
                        style={{ width: '100%' }}
                    >
                        {loading ? 'Creating Transfer...' : 'Create Wire Transfer'}
                    </button>
                </form>
            </div>
        </div>
    );
}

function TransferList({ transfers, onViewDetails, onRefresh }) {
    const getStatusColor = (status) => {
        switch (status) {
            case 'PENDING': return 'badge-warning';
            case 'VALIDATING': return 'badge-info';
            case 'PROCESSING': return 'badge-primary';
            case 'SETTLING': return 'badge-secondary';
            case 'COMPLETED': return 'badge-success';
            case 'FAILED': return 'badge-danger';
            default: return 'badge-primary';
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2>Transfer History</h2>
                    <button onClick={onRefresh} className="btn btn-secondary btn-sm">
                        Refresh
                    </button>
                </div>
            </div>
            <div className="card-body">
                {transfers.length === 0 ? (
                    <div className="alert alert-info">
                        No transfers found. Create your first transfer above.
                    </div>
                ) : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Debtor</th>
                                <th>Creditor</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transfers.map((transfer) => (
                                <tr key={transfer.id}>
                                    <td>
                                        <code style={{ fontSize: '12px' }}>{transfer.id.slice(0, 8)}...</code>
                                    </td>
                                    <td>{transfer.debtor_name}</td>
                                    <td>{transfer.creditor_name}</td>
                                    <td>
                                        {transfer.amount} {transfer.currency}
                                    </td>
                                    <td>
                                        <span className={`badge ${getStatusColor(transfer.status)}`}>
                                            {transfer.status}
                                        </span>
                                    </td>
                                    <td>
                                        {new Date(transfer.created_at).toLocaleDateString()}
                                    </td>
                                    <td>
                                        <button 
                                            className="btn btn-secondary btn-sm" 
                                            onClick={() => onViewDetails(transfer.id)}
                                        >
                                            View
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

function TransferDetailsModal({ transfer, isOpen, onClose }) {
    const [currentTransfer, setCurrentTransfer] = React.useState(null);
    const [activeMessageTab, setActiveMessageTab] = React.useState(0);

    React.useEffect(() => {
        setCurrentTransfer(transfer);
    }, [transfer]);

    // Poll for updates every second when modal is open
    React.useEffect(() => {
        if (!isOpen || !transfer) return;

        const interval = setInterval(async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/transfer/${transfer.id}`);
                setCurrentTransfer(response.data);
            } catch (error) {
                console.error('Error fetching transfer updates:', error);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [isOpen, transfer]);

    if (!currentTransfer) return null;

    const getStatusColor = (status) => {
        switch (status) {
            case 'PENDING': return 'badge-warning';
            case 'VALIDATING': return 'badge-info';
            case 'PROCESSING': return 'badge-primary';
            case 'SETTLING': return 'badge-secondary';
            case 'COMPLETED': return 'badge-success';
            case 'FAILED': return 'badge-danger';
            default: return 'badge-primary';
        }
    };

    return (
        <div className={`modal ${isOpen ? 'show' : ''}`} onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Transfer Details - {currentTransfer.id}</h2>
                    <button className="close" onClick={onClose}>&times;</button>
                </div>
                <div className="modal-body">
                    <div className="card" style={{ marginBottom: '20px' }}>
                        <div className="card-header">
                            <h3>Transfer Information</h3>
                        </div>
                        <div className="card-body">
                            <div style={{ display: 'grid', gap: '10px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <strong>Debtor:</strong>
                                    <span>{currentTransfer.debtor_name}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <strong>Creditor:</strong>
                                    <span>{currentTransfer.creditor_name}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <strong>Amount:</strong>
                                    <span>{currentTransfer.amount} {currentTransfer.currency}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <strong>Status:</strong>
                                    <span className={`badge ${getStatusColor(currentTransfer.status)}`}>
                                        {currentTransfer.status}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <strong>Created:</strong>
                                    <span>{new Date(currentTransfer.created_at).toLocaleString()}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Bank Account Information */}
                    {(currentTransfer.debtor_account || currentTransfer.creditor_account) && (
                        <div className="card" style={{ marginBottom: '20px' }}>
                            <div className="card-header">
                                <h3>Bank Account Balances</h3>
                            </div>
                            <div className="card-body">
                                <div style={{ display: 'grid', gap: '15px' }}>
                                    {currentTransfer.debtor_account && (
                                        <div style={{ 
                                            border: '1px solid #e9ecef',
                                            borderRadius: '8px',
                                            padding: '15px',
                                            backgroundColor: '#f8f9fa'
                                        }}>
                                            <h4 style={{ marginBottom: '10px', color: '#495057' }}>
                                                Debtor Account: {currentTransfer.debtor_account.account_holder}
                                            </h4>
                                            <div style={{ display: 'grid', gap: '5px', fontSize: '14px' }}>
                                                <div><strong>Account:</strong> {currentTransfer.debtor_account.account_id}</div>
                                                <div><strong>Balance:</strong> {currentTransfer.debtor_account.balance} {currentTransfer.debtor_account.currency}</div>
                                                <div><strong>Transactions:</strong> {currentTransfer.debtor_account.transactions.length}</div>
                                            </div>
                                        </div>
                                    )}
                                    
                                    {currentTransfer.creditor_account && (
                                        <div style={{ 
                                            border: '1px solid #e9ecef',
                                            borderRadius: '8px',
                                            padding: '15px',
                                            backgroundColor: '#f8f9fa'
                                        }}>
                                            <h4 style={{ marginBottom: '10px', color: '#495057' }}>
                                                Creditor Account: {currentTransfer.creditor_account.account_holder}
                                            </h4>
                                            <div style={{ display: 'grid', gap: '5px', fontSize: '14px' }}>
                                                <div><strong>Account:</strong> {currentTransfer.creditor_account.account_id}</div>
                                                <div><strong>Balance:</strong> {currentTransfer.creditor_account.balance} {currentTransfer.creditor_account.currency}</div>
                                                <div><strong>Transactions:</strong> {currentTransfer.creditor_account.transactions.length}</div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="card" style={{ marginBottom: '20px' }}>
                        <div className="card-header">
                            <h3>Processing Steps & Technical Details</h3>
                        </div>
                        <div className="card-body">
                            <div style={{ display: 'grid', gap: '15px' }}>
                                {currentTransfer.processing_steps && currentTransfer.processing_steps.map((step, index) => (
                                    <div key={index} style={{ 
                                        border: '1px solid #e9ecef',
                                        borderRadius: '8px',
                                        overflow: 'hidden'
                                    }}>
                                        <div style={{ 
                                            padding: '12px 16px',
                                            backgroundColor: '#f8f9fa',
                                            borderBottom: '1px solid #e9ecef',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '12px'
                                        }}>
                                            <span className={`badge ${getStatusColor(step.status)}`}>
                                                {step.status}
                                            </span>
                                            <span style={{ fontWeight: 'bold', fontSize: '14px' }}>
                                                {step.step}
                                            </span>
                                            <span style={{ 
                                                fontSize: '12px', 
                                                color: '#666',
                                                marginLeft: 'auto'
                                            }}>
                                                {new Date(step.timestamp).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        {step.details && (
                                            <div style={{ 
                                                padding: '16px',
                                                backgroundColor: 'white',
                                                fontSize: '13px',
                                                lineHeight: '1.5',
                                                color: '#495057'
                                            }}>
                                                {step.details}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* ISO 20022 Messages */}
                    <div className="card">
                        <div className="card-header">
                            <h3>ISO 20022 Messages</h3>
                        </div>
                        <div className="card-body">
                            <div className="tabs" style={{ marginBottom: '15px' }}>
                                <button 
                                    className={`tab ${activeMessageTab === 0 ? 'active' : ''}`}
                                    onClick={() => setActiveMessageTab(0)}
                                >
                                    PACS.008 (Credit Transfer)
                                </button>
                                {currentTransfer.pacs_002_xml && (
                                    <button 
                                        className={`tab ${activeMessageTab === 1 ? 'active' : ''}`}
                                        onClick={() => setActiveMessageTab(1)}
                                    >
                                        PACS.002 (Status Report)
                                    </button>
                                )}
                                {currentTransfer.pacs_004_xml && (
                                    <button 
                                        className={`tab ${activeMessageTab === 2 ? 'active' : ''}`}
                                        onClick={() => setActiveMessageTab(2)}
                                    >
                                        PACS.004 (Payment Return)
                                    </button>
                                )}
                                {currentTransfer.pacs_007_xml && (
                                    <button 
                                        className={`tab ${activeMessageTab === 3 ? 'active' : ''}`}
                                        onClick={() => setActiveMessageTab(3)}
                                    >
                                        PACS.007 (Cancellation)
                                    </button>
                                )}
                            </div>

                            <div className="tab-content" style={{ display: activeMessageTab === 0 ? 'block' : 'none' }}>
                                <div style={{ marginBottom: '15px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                                    <h4 style={{ marginBottom: '10px', color: '#495057' }}>PACS.008 - Financial Institution to Financial Institution Customer Credit Transfer</h4>
                                    <div style={{ fontSize: '13px', lineHeight: '1.5', color: '#666' }}>
                                        <p><strong>Purpose:</strong> Initiates a credit transfer between financial institutions on behalf of customers.</p>
                                        <p><strong>Key Elements:</strong></p>
                                        <ul style={{ marginLeft: '20px', marginTop: '5px' }}>
                                            <li><strong>GrpHdr:</strong> Message identification and control information</li>
                                            <li><strong>CdtTrfTxInf:</strong> Credit transfer transaction details</li>
                                            <li><strong>Dbtr/Cdtr:</strong> Debtor (sender) and Creditor (recipient) information</li>
                                            <li><strong>IntrBkSttlmAmt:</strong> Interbank settlement amount</li>
                                            <li><strong>DbtrAgt/CdtrAgt:</strong> Debtor and Creditor agent (banks)</li>
                                        </ul>
                                    </div>
                                </div>
                                <div className="xml-display">
                                    <pre>{currentTransfer.pacs_008_xml}</pre>
                                </div>
                            </div>

                            {currentTransfer.pacs_002_xml && (
                                <div className="tab-content" style={{ display: activeMessageTab === 1 ? 'block' : 'none' }}>
                                    <div style={{ marginBottom: '15px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                                        <h4 style={{ marginBottom: '10px', color: '#495057' }}>PACS.002 - Payment Status Report</h4>
                                        <div style={{ fontSize: '13px', lineHeight: '1.5', color: '#666' }}>
                                            <p><strong>Purpose:</strong> Confirms the status of a previously sent payment message.</p>
                                            <p><strong>Key Elements:</strong></p>
                                            <ul style={{ marginLeft: '20px', marginTop: '5px' }}>
                                                <li><strong>OrgnlGrpInf:</strong> References the original PACS.008 message</li>
                                                <li><strong>TxSts:</strong> Transaction status (ACSP = AcceptedSettlementCompleted)</li>
                                                <li><strong>StsRsnInf:</strong> Status reason information</li>
                                                <li><strong>OrgnlEndToEndId:</strong> Links to original end-to-end reference</li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div className="xml-display">
                                        <pre>{currentTransfer.pacs_002_xml}</pre>
                                    </div>
                                </div>
                            )}

                            {currentTransfer.pacs_004_xml && (
                                <div className="tab-content" style={{ display: activeMessageTab === 2 ? 'block' : 'none' }}>
                                    <div style={{ marginBottom: '15px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                                        <h4 style={{ marginBottom: '10px', color: '#495057' }}>PACS.004 - Payment Return</h4>
                                        <div style={{ fontSize: '13px', lineHeight: '1.5', color: '#666' }}>
                                            <p><strong>Purpose:</strong> Returns a payment that cannot be processed or needs to be reversed.</p>
                                            <p><strong>Key Elements:</strong></p>
                                            <ul style={{ marginLeft: '20px', marginTop: '5px' }}>
                                                <li><strong>RvslId:</strong> Unique reversal identifier</li>
                                                <li><strong>RtrdIntrBkSttlmAmt:</strong> Returned interbank settlement amount</li>
                                                <li><strong>RtrRsnInf:</strong> Return reason information</li>
                                                <li><strong>OrgnlTxId:</strong> References the original transaction</li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div className="xml-display">
                                        <pre>{currentTransfer.pacs_004_xml}</pre>
                                    </div>
                                </div>
                            )}

                            {currentTransfer.pacs_007_xml && (
                                <div className="tab-content" style={{ display: activeMessageTab === 3 ? 'block' : 'none' }}>
                                    <div style={{ marginBottom: '15px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                                        <h4 style={{ marginBottom: '10px', color: '#495057' }}>PACS.007 - Payment Cancellation Request</h4>
                                        <div style={{ fontSize: '13px', lineHeight: '1.5', color: '#666' }}>
                                            <p><strong>Purpose:</strong> Requests cancellation of a payment before it is settled.</p>
                                            <p><strong>Key Elements:</strong></p>
                                            <ul style={{ marginLeft: '20px', marginTop: '5px' }}>
                                                <li><strong>CxlId:</strong> Unique cancellation identifier</li>
                                                <li><strong>CxlRsnInf:</strong> Cancellation reason information</li>
                                                <li><strong>OrgnlTxId:</strong> References the original transaction</li>
                                                <li><strong>OrgnlGrpInf:</strong> Links to original message group</li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div className="xml-display">
                                        <pre>{currentTransfer.pacs_007_xml}</pre>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function AboutSection() {
    return (
        <div className="card">
            <div className="card-header">
                <h2>About Canadian Wire Transfer Simulator</h2>
            </div>
            <div className="card-body">
                <p style={{ marginBottom: '20px' }}>
                    This simulator demonstrates the Canadian wire transfer process using ISO 20022 
                    PACS.008 messages, reflecting the real-world implementation of Payments Canada's 
                    Lynx system and SWIFT messaging.
                </p>
                
                <hr style={{ margin: '20px 0' }} />
                
                <div style={{ marginBottom: '20px' }}>
                    <h3 style={{ marginBottom: '15px' }}>Transfer Process Steps:</h3>
                    <div style={{ display: 'grid', gap: '10px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span className="badge badge-primary">1</span>
                            <span>Customer initiates transfer with bank details</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span className="badge badge-primary">2</span>
                            <span>Bank validates and creates PACS.008 message</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span className="badge badge-primary">3</span>
                            <span>Message sent to Lynx (domestic) or SWIFT (international)</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span className="badge badge-primary">4</span>
                            <span>Clearing and settlement processing</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span className="badge badge-primary">5</span>
                            <span>Funds credited to beneficiary account</span>
                        </div>
                    </div>
                </div>
                
                <hr style={{ margin: '20px 0' }} />
                
                <div>
                    <h3 style={{ marginBottom: '15px' }}>ISO 20022 Message Types:</h3>
                    <div style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
                        <div>• <strong>PACS.008:</strong> Financial Institution to Financial Institution Customer Credit Transfer</div>
                        <div>• <strong>PACS.002:</strong> Payment Status Report (confirmation message)</div>
                        <div>• <strong>PACS.004:</strong> Payment Return (for failed transfers)</div>
                        <div>• <strong>PACS.007:</strong> Payment Cancellation Request</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root')); 
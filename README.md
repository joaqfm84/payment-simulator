# Canadian Wire Transfer Simulator

A Flask-based web application that simulates Canadian wire transfers using ISO 20022 PACS.008 messages, demonstrating the real-world implementation of Payments Canada's Lynx system and SWIFT messaging.

## Features

- **Interactive Transfer Creation**: Create wire transfers with Canadian banking details
- **ISO 20022 PACS.008 Generation**: Automatically generates compliant XML messages
- **Transfer History**: View and manage all created transfers
- **Detailed Transfer View**: Examine complete transfer details including XML messages
- **Modern UI**: React frontend with ChakraUI for a beautiful user experience
- **Educational Content**: Learn about the wire transfer process and message structure

## Technology Stack

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing support
- **lxml**: XML processing for ISO 20022 messages
- **uuid**: Unique identifier generation

### Frontend
- **React**: JavaScript library for building user interfaces
- **ChakraUI**: Modern component library for React
- **Axios**: HTTP client for API communication

## Project Structure

```
payment-simulator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/
│   └── index.html        # HTML template for React app
└── static/
    └── js/
        └── app.js        # React application
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Backend Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd payment-simulator
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask application**
   ```bash
   python app.py
   ```

The backend will start on `http://localhost:5000`

### Frontend Setup

The frontend is served directly by Flask and uses CDN-hosted React and ChakraUI libraries. No additional setup is required.

## API Endpoints

### GET /
Renders the home page with the React application.

### POST /create_transfer
Creates a new wire transfer and generates PACS.008 XML message.

**Request Body:**
```json
{
  "debtor_name": "John Doe",
  "institution_number": "003",
  "transit_number": "12345",
  "account_number": "1234567890",
  "creditor_name": "Jane Smith",
  "creditor_iban": "DE89370400440532013000",
  "creditor_bic": "COBADEFFXXX",
  "amount": 1000.00,
  "currency": "CAD",
  "purpose": "Payment for services"
}
```

**Response:**
```json
{
  "message": "Transfer created successfully",
  "transfer_id": "uuid-string",
  "transfer": {
    "id": "uuid-string",
    "debtor_name": "John Doe",
    "institution_number": "003",
    "transit_number": "12345",
    "account_number": "1234567890",
    "creditor_name": "Jane Smith",
    "creditor_iban": "DE89370400440532013000",
    "creditor_bic": "COBADEFFXXX",
    "amount": 1000.00,
    "currency": "CAD",
    "purpose": "Payment for services",
    "created_at": "2024-01-01T12:00:00",
    "status": "PENDING",
    "pacs_008_xml": "<?xml version=\"1.0\" ?>..."
  }
}
```

### GET /transfers
Lists all created transfers.

**Response:**
```json
{
  "transfers": [
    {
      "id": "uuid-string",
      "debtor_name": "John Doe",
      "creditor_name": "Jane Smith",
      "amount": 1000.00,
      "currency": "CAD",
      "status": "PENDING",
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "count": 1
}
```

### GET /transfer/<transfer_id>
Retrieves detailed information for a specific transfer.

**Response:**
```json
{
  "id": "uuid-string",
  "debtor_name": "John Doe",
  "institution_number": "003",
  "transit_number": "12345",
  "account_number": "1234567890",
  "creditor_name": "Jane Smith",
  "creditor_iban": "DE89370400440532013000",
  "creditor_bic": "COBADEFFXXX",
  "amount": 1000.00,
  "currency": "CAD",
  "purpose": "Payment for services",
  "created_at": "2024-01-01T12:00:00",
  "status": "PENDING",
  "pacs_008_xml": "<?xml version=\"1.0\" ?>..."
}
```

## ISO 20022 PACS.008 Message Structure

The application generates ISO 20022 PACS.008 messages with the following structure:

- **Document Root**: Contains namespace declarations for ISO 20022
- **FIToFICstmrCdtTrf**: Financial Institution to Financial Institution Customer Credit Transfer
- **GrpHdr**: Group header with message identification and control information
- **CdtTrfTxInf**: Credit transfer transaction information including:
  - Payment identification (InstrId, EndToEndId)
  - Interbank settlement amount and currency
  - Debtor and creditor information
  - Account details (Canadian routing numbers, IBAN)
  - Remittance information

## Canadian Banking Information

The simulator supports Canadian banking details:
- **Institution Number**: 3-digit code identifying the financial institution
- **Transit Number**: 5-digit code identifying the specific branch
- **Account Number**: Customer's account number

## Wire Transfer Process

1. **Initiation**: Customer provides transfer details
2. **Validation**: Bank validates account information and transfer details
3. **Message Creation**: System generates ISO 20022 PACS.008 message
4. **Transmission**: Message sent to Lynx (domestic) or SWIFT (international)
5. **Clearing**: Payment clearing and settlement processing
6. **Settlement**: Funds credited to beneficiary account

## Usage

1. **Start the application**: Run `python app.py`
2. **Open browser**: Navigate to `http://localhost:5000`
3. **Create transfer**: Fill out the transfer form with required details
4. **View transfers**: Check the "View Transfers" tab to see all transfers
5. **Examine details**: Click "View" on any transfer to see the generated PACS.008 XML

## Development

### Adding New Features
- Backend: Modify `app.py` to add new routes or functionality
- Frontend: Edit `static/js/app.js` to update the React components
- Templates: Update `templates/index.html` for structural changes

### Testing
- The application includes basic error handling and validation
- Test transfer creation with various input combinations
- Verify XML generation for different currencies and amounts

## Production Considerations

For production deployment, consider:
- Database integration (PostgreSQL, MySQL) instead of in-memory storage
- Authentication and authorization
- Input validation and sanitization
- Logging and monitoring
- HTTPS enforcement
- Rate limiting
- API documentation (Swagger/OpenAPI)

## License

This project is for educational and demonstration purposes.

## Contributing

Feel free to submit issues and enhancement requests! 
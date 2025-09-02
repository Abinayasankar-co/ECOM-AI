# 🤖 AI Assistant

A powerful AI-powered product analysis and query assistant that combines web scraping, Neo4j graph database, and natural language processing to help you analyze e-commerce products.

## ✨ Features

- **🛒 Web Scraping**: Automatically scrape product information from e-commerce websites
- **🗄️ Graph Database**: Store and query product data using Neo4j
- **🤖 AI-Powered Queries**: Ask questions in natural language and get intelligent responses
- **🎤 Voice Interface**: Text-to-speech functionality for hands-free interaction
- **📊 Beautiful UI**: Modern, responsive interface built with Streamlit
- **🔍 Smart Product Detection**: Automatically detects products using multiple selectors

## 🏗️ Project Structure

```
project-root/
│
├── .env                    # Environment variables
├── .gitignore             # Git ignore file
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── llm/
│   └── query.py          # LLM query generation
├── db/
│   └── neo4j_client.py   # Neo4j database operations
├── utils/
│   └── tts.py           # Text-to-speech utilities
└── ui/
    └── components.py     # UI components and styling
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Neo4j Database (local or cloud)
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ECOM-AI-Rasss
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Copy the example environment file and configure it:
   ```bash
   cp env.example .env
   ```
   
   Edit the `.env` file with your actual credentials:
   ```env
   # Neo4j Database Configuration
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_neo4j_password_here
   
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Start Neo4j Database**
   - Install Neo4j Desktop or use Neo4j AuraDB
   - Create a new database
   - Note down the connection details

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🎯 Usage

### 1. Scraping Products

1. Open the application in your browser
2. Enter a product listing URL from any e-commerce site
3. Click "🚀 Scrape Products"
4. The system will automatically detect and extract product information
5. Products are stored in Neo4j with relationships and properties

### 2. Querying Products

1. Use the chat interface to ask questions about your products
2. Examples:
   - "Show me all products under $50"
   - "What are the highest rated products?"
   - "Find products from Amazon"
   - "Which products have 5-star ratings?"

3. The AI will generate Cypher queries and return results
4. Results are displayed with voice feedback

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `NEO4J_URI` | Neo4j database URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Required |

### Database Schema

The application creates the following schema in Neo4j:

```cypher
// Product nodes
(:Product {
  title: String,
  price: String,
  star_rating: String,
  store: String,
  created_at: DateTime
})
```

## 🛠️ Technical Details

### Dependencies

- **Streamlit**: Web application framework
- **LangChain**: LLM integration and query generation
- **Neo4j**: Graph database for product storage
- **BeautifulSoup**: Web scraping
- **pyttsx3**: Text-to-speech synthesis
- **Requests**: HTTP requests for web scraping

### Architecture

1. **Web Scraping Module**: Uses BeautifulSoup with multiple selectors for robust product detection
2. **Database Layer**: Neo4j client with connection pooling and error handling
3. **LLM Integration**: OpenAI GPT-4 for natural language to Cypher query conversion
4. **UI Layer**: Streamlit with custom components and responsive design
5. **TTS Module**: Voice synthesis and playback with cleanup

## 🐛 Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Check if Neo4j is running
   - Verify connection details in `.env`
   - Ensure firewall allows connection

2. **URI Scheme Error: "URI scheme b'' is not supported"**
   - This error occurs when environment variables are not properly set
   - Solution: Create a `.env` file with proper Neo4j credentials
   - Ensure the `.env` file is in the project root directory
   - Check that there are no extra spaces or quotes in the `.env` file
   - Example correct format:
     ```
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=your_password
     ```

2. **OpenAI API Errors**
   - Verify API key is correct
   - Check API quota and billing
   - Ensure internet connection

3. **Scraping Issues**
   - Some websites may block automated requests
   - Try different URLs or check site structure
   - Consider using different user agents

4. **Audio Issues**
   - Install system audio drivers
   - Check microphone permissions
   - Verify pyttsx3 installation

### Error Logs

The application includes comprehensive logging. Check the console output for detailed error messages.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Neo4j for graph database
- Streamlit for the web framework
- BeautifulSoup for web scraping capabilities

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Happy Product Analysis! 🎉** 
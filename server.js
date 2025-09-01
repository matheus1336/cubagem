import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Sample product data
const products = [
    {
        "codigo": "J-315",
        "nome": "Jacuzzi J-315",
        "comprimento": 213,
        "largura": 213,
        "altura": 91,
        "peso": 340
    },
    {
        "codigo": "J-325",
        "nome": "Jacuzzi J-325",
        "comprimento": 229,
        "largura": 229,
        "altura": 94,
        "peso": 385
    },
    {
        "codigo": "J-335",
        "nome": "Jacuzzi J-335",
        "comprimento": 244,
        "largura": 229,
        "altura": 97,
        "peso": 430
    },
    {
        "codigo": "J-345",
        "nome": "Jacuzzi J-345",
        "comprimento": 244,
        "largura": 244,
        "altura": 97,
        "peso": 475
    },
    {
        "codigo": "J-355",
        "nome": "Jacuzzi J-355",
        "comprimento": 244,
        "largura": 244,
        "altura": 97,
        "peso": 520
    }
];

// Box configurations
const boxes = [
    {
        "nome": "Caixa Pequena",
        "volume_max": 2.0,
        "peso_max": 500
    },
    {
        "nome": "Caixa Média",
        "volume_max": 5.0,
        "peso_max": 1000
    },
    {
        "nome": "Caixa Grande",
        "volume_max": 10.0,
        "peso_max": 2000
    }
];

// Routes
app.get('/', (req, res) => {
    res.sendFile(join(__dirname, 'templates', 'index.html'));
});

app.get('/api/search', (req, res) => {
    const query = req.query.q?.toLowerCase() || '';
    
    if (!query) {
        return res.json([]);
    }
    
    const results = products.filter(product => 
        product.codigo.toLowerCase().includes(query) || 
        product.nome.toLowerCase().includes(query)
    );
    
    res.json(results);
});

app.post('/api/calculate', (req, res) => {
    const { selectedProducts } = req.body;
    
    if (!selectedProducts || !Array.isArray(selectedProducts)) {
        return res.status(400).json({ error: 'Invalid input' });
    }
    
    let totalVolume = 0;
    let totalWeight = 0;
    
    selectedProducts.forEach(productCode => {
        const product = products.find(p => p.codigo === productCode);
        if (product) {
            const volume = (product.comprimento * product.largura * product.altura) / 1000000; // Convert to m³
            totalVolume += volume;
            totalWeight += product.peso;
        }
    });
    
    const suitableBoxes = boxes.filter(box => 
        box.volume_max >= totalVolume && box.peso_max >= totalWeight
    );
    
    res.json({
        totalVolume: totalVolume.toFixed(3),
        totalWeight,
        suitableBoxes
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
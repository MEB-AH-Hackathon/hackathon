Test with this command: 

curl -X POST http://localhost:3001/fda -H "Content-Type: application/json" -d "{\"tool\":\"searchValidatedSymptoms\",\"params\":{\"vaccine\":\"COVID-19\",\"symptoms\":[\"fever\",\"headache\"]}}"
#!/usr/bin/env node

const axios = require('axios');

async function debugHttpResponse() {
    try {
        console.log('Testing HTTP wrapper response structure...');
        
        const response = await axios.post('http://localhost:3001/tools/search_conversations_unified', {
            arguments: {
                query: "test",
                limit: 1
            }
        });
        
        console.log('\n=== RAW HTTP RESPONSE ===');
        console.log('response.status:', response.status);
        console.log('response.data keys:', Object.keys(response.data));
        console.log('response.data.result keys:', Object.keys(response.data.result || {}));
        
        console.log('\n=== RESPONSE.DATA ===');
        console.log(JSON.stringify(response.data, null, 2));
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

debugHttpResponse();
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';

const TradeFinanceApp = () => {
  const [lcs, setLCs] = useState([]);
  const [newLC, setNewLC] = useState({
    seller: '',
    sellerBank: '',
    amount: '',
    expiryDays: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:5000/api';

  const createLC = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/lc/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLC),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error);

      setLCs([...lcs, { ...newLC, id: data.lcId }]);
      setNewLC({ seller: '', sellerBank: '', amount: '', expiryDays: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const submitDocuments = async (lcId, files) => {
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('documents', files[0]);

    try {
      const response = await fetch(`${API_URL}/lc/submit-documents/${lcId}`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error);

      // Update LC status in UI
      setLCs(lcs.map(lc => 
        lc.id === lcId ? { ...lc, documentHash: data.documentHash } : lc
      ));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Create Letter of Credit</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={createLC} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Seller Address</label>
              <Input
                type="text"
                value={newLC.seller}
                onChange={(e) => setNewLC({ ...newLC, seller: e.target.value })}
                placeholder="0x..."
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Seller Bank Address</label>
              <Input
                type="text"
                value={newLC.sellerBank}
                onChange={(e) => setNewLC({ ...newLC, sellerBank: e.target.value })}
                placeholder="0x..."
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Amount (ETH)</label>
              <Input
                type="number"
                value={newLC.amount}
                onChange={(e) => setNewLC({ ...newLC, amount: e.target.value })}
                placeholder="0.0"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Expiry Days</label>
              <Input
                type="number"
                value={newLC.expiryDays}
                onChange={(e) => setNewLC({ ...newLC, expiryDays: e.target.value })}
                placeholder="30"
                required
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create LC'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Active Letters of Credit</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {lcs.map((lc) => (
              <div key={lc.id} className="p-4 border rounded">
                <h3 className="font-medium">LC #{lc.id}</h3>
                <div className="mt-2 space-y-1 text-sm">
                  <p>Seller: {lc.seller}</p>
                  <p>Amount: {lc.amount} ETH</p>
                  <p>Expiry: {lc.expiryDays} days</p>
                  {lc.documentHash && <p>Document Hash: {lc.documentHash}</p>}
                </div>
                {!lc.documentHash && (
                  <div className="mt-4">
                    <Input
                      type="file"
                      onChange={(e) => submitDocuments(lc.id, e.target.files)}
                      className="mb-2"
                    />
                  </div>
                )}
              </div>
            ))}
            {lcs.length === 0 && (
              <p className="text-gray-500">No active letters of credit</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TradeFinanceApp;

import React, { useEffect, useState } from 'react';
import axios from 'axios';
 
function App() {
  const [file, setFile] = useState(null);
 
  const handleChange = (e) => {
setFile(e.target.files[0]);
  };

 
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
 
    const formData = new FormData();
    formData.append('file', file);
 
    try {
const res = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    console.log(res.data);
      alert("Upload successful!");
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Upload failed.");
    }
  };

 
  return (
    <div style={{height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', marginLeft: '500px'}}>
      <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '20px', padding: '40px', border: '1px solid #ccc', borderRadius: '12px', backgroundColor: '#fff'}}>
      <input type="file" onChange={handleChange} style={{fontSize: '16px', padding: '10px', borderRadius: '8px', border: '1px solid #ccc', cursor: 'pointer'}} />
      <button type="submit" style={{backgroundColor: 'gray'}}>Upload</button>
    </form>
    </div>
  );
}
 
export default App;

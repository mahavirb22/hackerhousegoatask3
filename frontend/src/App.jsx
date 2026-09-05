import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, ShieldCheck, ShieldAlert, CheckCircle, ExternalLink, RefreshCw, AlertTriangle, ArrowRight, Lock, Eye, ScanFace } from 'lucide-react';

export default function App() {
  const [currentStep, setCurrentStep] = useState(1); // 1: Capture/Upload, 2: Match Candidates, 3: On-Chain Result
  const [inputMode, setInputMode] = useState('upload'); // 'upload' or 'camera'

  // Image & File State
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Camera State
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  // Scan & Job State
  const [jobId, setJobId] = useState(null);
  const [jobState, setJobState] = useState(null); // ScanJob status object from /api/scan/status/{job_id}
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Confirmation & Tamper State
  const [confirmResult, setConfirmResult] = useState(null);
  const [tamperResult, setTamperResult] = useState(null);

  // Camera Stream Management
  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720, facingMode: 'user' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setCameraError('Camera access denied or unavailable. Please upload an image file instead.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  useEffect(() => {
    if (inputMode === 'camera') {
      startCamera();
    } else {
      stopCamera();
    }
    return () => stopCamera();
  }, [inputMode]);

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
          setSelectedFile(file);
          setPreviewUrl(URL.createObjectURL(blob));
          stopCamera();
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setErrorMsg(null);
    }
  };

  // Step 1 -> Step 2: Start Scan Job & Poll Progress
  const handleStartScan = async () => {
    if (!selectedFile) {
      setErrorMsg('Please select or capture a subject face image first.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('similarity_threshold', '0.65');
      formData.append('social_only', 'false');
      formData.append('top_k', '3');

      const startRes = await fetch('/api/scan', {
        method: 'POST',
        body: formData,
      }).then(r => r.json());

      if (startRes.job_id) {
        setJobId(startRes.job_id);
        pollJobStatus(startRes.job_id);
      } else {
        throw new Error(startRes.detail || 'Failed to start scan job.');
      }
    } catch (err) {
      setErrorMsg(err.message);
      setLoading(false);
    }
  };

  const pollJobStatus = (id) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/scan/status/${id}`).then(r => r.json());
        setJobState(res);

        if (res.status === 'completed') {
          clearInterval(interval);
          setLoading(false);
          setCurrentStep(2); // Advance smoothly to Step 2
        } else if (res.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
          setErrorMsg(res.error || res.message || 'Scan failed.');
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 800);
  };

  // Step 2 -> Step 3: Confirm Selected Match (Phase 4)
  const handleConfirmMatch = async (candUrl, candIndex) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          candidate_url: candUrl,
          candidate_index: candIndex,
        }),
      }).then(r => r.json());

      if (res.status === 'success') {
        setConfirmResult(res);
        setLoading(false);
        setCurrentStep(3); // Advance smoothly to Step 3
      } else {
        throw new Error(res.detail || 'Confirmation failed.');
      }
    } catch (err) {
      setErrorMsg(err.message);
      setLoading(false);
    }
  };

  // Step 3 Standout: Run Tamper Test
  const handleRunTamperTest = async () => {
    try {
      const targetHash = confirmResult?.data_hash || '0xb32a3e3179c1a3f4087802040b22435534e0168f0a6c60e3fac7b94309cce8ac';
      const res = await fetch('/api/tamper-demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ record_id: targetHash }),
      }).then(r => r.json());
      setTamperResult(res);
    } catch (err) {
      console.error('Tamper demo error:', err);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setSelectedFile(null);
    setPreviewUrl(null);
    setJobId(null);
    setJobState(null);
    setConfirmResult(null);
    setTamperResult(null);
    setErrorMsg(null);
  };

  return (
    <div className="forensic-app">
      {/* Hidden Canvas for Camera Captures */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Professional Header Navigation Bar */}
      <header className="top-bar">
        <div className="brand-badge-logo">
          <div className="logo-icon-box">
            <ScanFace size={22} />
          </div>
          <h1>Forensic Eye</h1>
          <span className="tag-live" style={{ marginLeft: '0.4rem' }}>
            <span className="pulsing-dot"></span>
            Polygon Amoy Verified
          </span>
        </div>

        {/* 3-Step Wizard Single-Line Stepper */}
        <nav className="stepper-nav">
          <div className={`step-item ${currentStep === 1 ? 'active' : currentStep > 1 ? 'completed' : ''}`}>
            <span className="step-num">1</span>
            <span>Face Scan</span>
          </div>
          <div className={`step-item ${currentStep === 2 ? 'active' : currentStep > 2 ? 'completed' : ''}`}>
            <span className="step-num">2</span>
            <span>Matches</span>
          </div>
          <div className={`step-item ${currentStep === 3 ? 'active' : ''}`}>
            <span className="step-num">3</span>
            <span>On-Chain Record</span>
          </div>
        </nav>
      </header>

      {/* Error Alert Box */}
      {errorMsg && (
        <div style={{ background: '#FEF2F2', border: '1px solid var(--border-red)', color: '#DC2626', padding: '1rem 1.25rem', borderRadius: '12px', marginBottom: '1.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 500 }}>
          <AlertTriangle size={20} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* =================================================================== */}
      {/* STEP 1: Face Capture & Upload Screen                                */}
      {/* =================================================================== */}
      {currentStep === 1 && (
        <div className="screen-card">
          <div className="screen-header">
            <h2 className="screen-title">1. Capture or Upload Subject Face</h2>
            <p className="screen-subtitle">Use live camera feed or upload a photo to extract 128-d facial embedding vectors.</p>
          </div>

          {/* Input Mode Switcher */}
          <div className="tab-switcher">
            <button className={`tab-btn ${inputMode === 'upload' ? 'active' : ''}`} onClick={() => setInputMode('upload')}>
              <Upload size={16} /> File Upload
            </button>
            <button className={`tab-btn ${inputMode === 'camera' ? 'active' : ''}`} onClick={() => setInputMode('camera')}>
              <Camera size={16} /> Live Camera Feed
            </button>
          </div>

          {/* Upload Dropzone */}
          {inputMode === 'upload' && (
            <div>
              {previewUrl ? (
                <div style={{ textAlign: 'center' }}>
                  <img src={previewUrl} alt="Subject Face Preview" className="upload-preview-img" />
                  <div style={{ marginTop: '1.25rem' }}>
                    <button className="btn-secondary" onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}>
                      <RefreshCw size={14} /> Change Photo
                    </button>
                  </div>
                </div>
              ) : (
                <label className="dropzone">
                  <Upload size={40} style={{ color: 'var(--accent-orange)', marginBottom: '0.85rem' }} />
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
                    Drop subject face photo here, or click to browse
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                    Supports JPG, PNG, WEBP (Minimum 60×60 px face resolution)
                  </p>
                  <input type="file" accept="image/*" onChange={handleFileSelect} style={{ display: 'none' }} />
                </label>
              )}
            </div>
          )}

          {/* Camera Viewfinder */}
          {inputMode === 'camera' && (
            <div>
              {cameraError ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#DC2626', background: '#FEF2F2', borderRadius: '12px' }}>{cameraError}</div>
              ) : (
                <div>
                  <div className="camera-viewfinder">
                    <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
                    <div className="reticle-overlay" />
                    <div className="scanline" />
                  </div>
                  <div style={{ marginTop: '1.25rem', textAlign: 'center' }}>
                    <button className="btn-primary" onClick={capturePhoto} disabled={!isCameraActive}>
                      <Camera size={18} /> Capture Snapshot
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Start Scan Trigger Button */}
          {previewUrl && !loading && (
            <div style={{ marginTop: '2rem', textAlign: 'right' }}>
              <button className="btn-primary" onClick={handleStartScan}>
                Scan Face & Search Web <ArrowRight size={18} />
              </button>
            </div>
          )}

          {/* Progress Bar & Status Polling */}
          {loading && jobState && (
            <div className="progress-box">
              <div className="progress-bar-track">
                <div className="progress-bar-fill" style={{ width: `${jobState.progress_pct || 15}%` }} />
              </div>
              <div className="progress-info">
                <span>{jobState.message}</span>
                <span>{jobState.progress_pct || 15}%</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =================================================================== */}
      {/* STEP 2: Candidate Matching Cards Screen                              */}
      {/* =================================================================== */}
      {currentStep === 2 && jobState && jobState.results && (
        <div className="screen-card">
          <div className="screen-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 className="screen-title">2. Candidate Matching Pages</h2>
              <p className="screen-subtitle">Ranked visual matches filtered to social platforms (X, Instagram, LinkedIn, Reddit).</p>
            </div>
            <button className="btn-secondary" onClick={handleReset}>
              <RefreshCw size={14} /> New Scan
            </button>
          </div>

          <div className="candidates-list">
            {jobState.results.reverse_search.top_candidates.map((cand, idx) => (
              <div key={idx} className="candidate-card">
                <img src={cand.thumbnail} alt={cand.title} className="cand-thumb" />
                <div className="cand-details">
                  <div>
                    <div className="cand-top">
                      <span className="domain-badge">{cand.source_domain}</span>
                      <span className="sim-score-badge">
                        {(cand.facial_similarity_score * 100).toFixed(1)}% Cosine Match
                      </span>
                    </div>
                    <h3 className="cand-title">{cand.title}</h3>
                  </div>

                  <div className="cand-actions">
                    <a href={cand.url} target="_blank" rel="noopener noreferrer" className="link-out">
                      Inspect Source Page <ExternalLink size={14} />
                    </a>
                    <button className="btn-primary" style={{ padding: '0.6rem 1.25rem', fontSize: '0.875rem' }} onClick={() => handleConfirmMatch(cand.url, idx)} disabled={loading}>
                      <Lock size={15} /> Verify & Record On-Chain
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {loading && (
            <div className="progress-box">
              <div className="progress-info">
                <span>Phase 4: Submitting record to Polygon Amoy smart contract...</span>
                <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* =================================================================== */}
      {/* STEP 3: On-Chain Verification & Tamper Test Result Screen           */}
      {/* =================================================================== */}
      {currentStep === 3 && confirmResult && (
        <div className="screen-card">
          <div className="screen-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--accent-emerald)', marginBottom: '0.5rem' }}>
              <CheckCircle size={24} />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.04em' }}>IMMUTABLE RECORD STORED ON POLYGON AMOY</span>
            </div>
            <h2 className="screen-title">3. On-Chain Verification Record</h2>
            <p className="screen-subtitle">Face metadata and SHA-256 data hash successfully committed to smart contract.</p>
            <div style={{ marginTop: '0.65rem', background: '#F1F5F9', border: '1px solid #E2E8F0', padding: '0.4rem 0.85rem', borderRadius: '20px', display: 'inline-flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.775rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              <ShieldCheck size={14} style={{ color: 'var(--accent-orange)' }} />
              <span>GDPR-Compliant: Raw 128-d biometric vectors are salted & hashed. Zero biometrics exposed on-chain.</span>
            </div>
          </div>

          {/* On-Chain Hashes & CIDs */}
          <div className="result-hash-box">
            <div className="hash-row">
              <span className="hash-label">Transaction Hash</span>
              <span className="hash-val">{confirmResult.transaction_hash}</span>
            </div>
            <div className="hash-row">
              <span className="hash-label">IPFS CID</span>
              <span className="hash-val">{confirmResult.ipfs_cid}</span>
            </div>
            <div className="hash-row">
              <span className="hash-label">Data Hash (bytes32)</span>
              <span className="hash-val">{confirmResult.data_hash}</span>
            </div>
            <div className="hash-row">
              <span className="hash-label">Submitter Wallet</span>
              <span className="hash-val">{confirmResult.submitter}</span>
            </div>
          </div>

          {/* Action Links & Buttons */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
            <a href={confirmResult.polygonscan_link} target="_blank" rel="noopener noreferrer" className="btn-primary" style={{ textDecoration: 'none' }}>
              <ExternalLink size={16} /> View on Polygonscan
            </a>
            <button className="btn-danger" onClick={handleRunTamperTest}>
              <ShieldAlert size={16} /> Run Tamper Test
            </button>
            <button className="btn-secondary" onClick={handleReset}>
              <RefreshCw size={14} /> Start New Scan
            </button>
          </div>

          {/* Standout Tamper Detection Output */}
          {tamperResult && (
            <div className="tamper-fail-card">
              <div className="tamper-header">
                <ShieldAlert size={28} />
                <span>STANDOUT DEMO: TAMPER VERIFICATION FAILED!</span>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                {tamperResult.message}
              </p>

              <div className="result-hash-box" style={{ background: '#FFFFFF', borderColor: 'var(--border-red)' }}>
                <div className="hash-row">
                  <span className="hash-label" style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>IMMUTABLE ON-CHAIN HASH</span>
                  <span className="hash-val" style={{ color: 'var(--text-main)' }}>{tamperResult.original_on_chain_hash}</span>
                </div>
                <div className="hash-row">
                  <span className="hash-label" style={{ color: 'var(--accent-red)', fontWeight: 700 }}>MUTATED RECOMPUTED HASH</span>
                  <span className="hash-val" style={{ color: 'var(--accent-red)' }}>{tamperResult.tampered_recomputed_hash}</span>
                </div>
              </div>

              <div style={{ fontSize: '0.825rem', color: '#B45309', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                Mutation Detail: {tamperResult.mutation_details} | Match Boolean: <strong>FALSE (Tamper Detected)</strong>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

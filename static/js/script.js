/**
 * NextHire AI - Unified Interactive Client Logic
 */

document.addEventListener('DOMContentLoaded', () => {

  // Register Service Worker for PWA compliance
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js', { scope: '/' })
        .then((reg) => {
          console.log('[PWA] Service Worker registered with scope:', reg.scope);
        })
        .catch((err) => {
          console.log('[PWA] Service Worker registration failed:', err);
        });
    });

    // Reload the page automatically when a new service worker takes control
    let refreshing = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (!refreshing) {
        refreshing = true;
        window.location.reload();
      }
    });
  }

  // Mobile Hamburger Menu Navigation Toggle
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const navElement = document.querySelector('header nav');
  if (hamburgerBtn && navElement) {
    hamburgerBtn.addEventListener('click', () => {
      hamburgerBtn.classList.toggle('active');
      navElement.classList.toggle('active');
    });
    
    // Auto collapse menu when a navigation item is clicked
    const navLinks = navElement.querySelectorAll('ul li a');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        hamburgerBtn.classList.remove('active');
        navElement.classList.remove('active');
      });
    });
  }

  // ==========================================
  // --- 1. Global Mouse Light Glow Tracker ---
  // ==========================================
  const mouseGlow = document.getElementById('mouseGlow');
  window.addEventListener('mousemove', (e) => {
    document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
    document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`);
  });

  // ==========================================
  // --- 2. Global Toast Notification Box ---
  // ==========================================
  const toastBox = document.getElementById('toastBox');
  const toastTitle = document.getElementById('toastTitle');
  const toastMessage = document.getElementById('toastMessage');
  let toastTimeout;

  function showToast(title, message) {
    clearTimeout(toastTimeout);
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    toastBox.classList.add('active');
    
    toastTimeout = setTimeout(() => {
      toastBox.classList.remove('active');
    }, 4500);
  }

  // Welcome alerts
  if (document.querySelector('.dashboard-body')) {
    setTimeout(() => {
      showToast('WORKSPACE SYNCED', 'John Doe profile data fetched from database.');
    }, 1200);
  } else {
    setTimeout(() => {
      showToast('SYSTEM ACTIVE', 'NextHire AI platform initialized successfully.');
    }, 1000);
  }

  // ==========================================
  // --- 3. Landing Page: Toggleable Pricing ---
  // ==========================================
  const priceToggle = document.getElementById('priceToggle');
  const proPrice = document.getElementById('proPrice');

  if (priceToggle && proPrice) {
    let isAnnual = false;
    priceToggle.addEventListener('click', () => {
      isAnnual = !isAnnual;
      priceToggle.classList.toggle('active');
      
      if (isAnnual) {
        proPrice.innerHTML = `$23<span class="price-period">/mo</span>`;
        showToast('BILLING SETTINGS', 'Annual billing calculations mapped (Save 20%).');
      } else {
        proPrice.innerHTML = `$29<span class="price-period">/mo</span>`;
        showToast('BILLING SETTINGS', 'Monthly billing calculations mapped.');
      }
    });
  }

  // ==========================================
  // --- 4. Landing Page: FAQ Accordion ---
  // ==========================================
  const faqTriggers = document.querySelectorAll('.faq-trigger');
  
  faqTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const item = trigger.parentNode;
      const panel = trigger.nextElementSibling;
      const isActive = item.classList.contains('active');
      
      // Close all other panels
      document.querySelectorAll('.faq-item').forEach(otherItem => {
        otherItem.classList.remove('active');
        otherItem.querySelector('.faq-panel').style.maxHeight = null;
      });

      // Toggle current panel
      if (!isActive) {
        item.classList.add('active');
        panel.style.maxHeight = panel.scrollHeight + 'px';
      }
    });
  });

  // ==========================================
  // --- 5. 3D Card Hover Tilt Calculations ---
  // ==========================================
  const wrappers = document.querySelectorAll('.card-3d-wrapper');
  wrappers.forEach(wrap => {
    const card = wrap.querySelector('.holo-3d-card, .auth-card');
    if (card) {
      wrap.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const cardWidth = rect.width;
        const cardHeight = rect.height;
        const mouseX = e.clientX - rect.left - cardWidth / 2;
        const mouseY = e.clientY - rect.top - cardHeight / 2;
        
        const rotateX = -(mouseY / (cardHeight / 2)) * 10;
        const rotateY = (mouseX / (cardWidth / 2)) * 10;
        
        card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      });

      wrap.addEventListener('mouseleave', () => {
        card.style.transform = 'rotateX(0deg) rotateY(0deg)';
        card.style.transition = 'transform 0.5s ease';
      });

      wrap.addEventListener('mouseenter', () => {
        card.style.transition = 'transform 0.1s ease';
      });
    }
  });

  // ==========================================
  // --- 6. Dashboard SPA Views Switcher ---
  // ==========================================
  const menuItems = document.querySelectorAll('.menu-item');
  
  window.switchTab = function(tabName) {
    const targetItem = document.querySelector(`.menu-item[data-tab="${tabName}"]`);
    if (targetItem) {
      // Clear active states
      menuItems.forEach(item => item.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
      
      // Activate target states
      targetItem.classList.add('active');
      document.getElementById(`${tabName}-tab`).classList.add('active');
      
      showToast('NAVIGATION', `WORKSPACE -> ${tabName.toUpperCase()} tab active.`);
    }
  }

  menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tabName = item.getAttribute('data-tab');
      switchTab(tabName);
    });
  });

  // ==========================================
  // --- 7. Dashboard: Resume Analyzer Scanner ---
  // ==========================================
  const uploadZone = document.getElementById('uploadZone');
  const resumeFileInput = document.getElementById('resumeFileInput');
  const gaugeContainer = document.getElementById('gaugeContainer');
  const gaugeCircle = document.getElementById('gaugeCircle');
  const scoreVal = document.getElementById('scoreVal');
  const terminalLogs = document.getElementById('terminalLogs');
  const insightsDashboard = document.getElementById('insightsDashboard');
  const scanTriggerBtn = document.getElementById('scanTriggerBtn');
  const downloadReportBtn = document.getElementById('downloadReportBtn');
  const holoCard = document.getElementById('holoCard');

  function uploadAndScanResume(file) {
    if (!file) return;
    
    if (holoCard) holoCard.classList.add('is-scanning');
    uploadZone.style.display = 'none';
    gaugeContainer.classList.remove('active');
    insightsDashboard.classList.remove('active');
    terminalLogs.classList.add('active');
    terminalLogs.innerHTML = '';

    const logs = [
      `[NODE] CONNECTING TO SECURE FILE SYSTEM...`,
      `[SCAN] ANALYZING FILE STRUCTURE: ${file.name.toUpperCase()}`,
      `[PARSE] EXTRACTING METRICS & PARSING ENTITIES...`,
      `[MATCH] VERIFYING RELEVANT COMPETENCY MATRICES...`,
      `[ALIGN] COMPILING JOB PROFILE STRENGTHS...`
    ];

    let logIdx = 0;
    const interval = setInterval(() => {
      if (logIdx < logs.length) {
        const row = document.createElement('div');
        row.className = 'log-row';
        row.textContent = logs[logIdx];
        terminalLogs.appendChild(row);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
        logIdx++;
      } else {
        clearInterval(interval);
        
        // Start upload and fetch results
        const formData = new FormData();
        formData.append('file', file);
        
        const row = document.createElement('div');
        row.className = 'log-row';
        row.textContent = `[UPLOAD] SENDING TO NESTHIRE AI API ENGINE...`;
        terminalLogs.appendChild(row);

        fetch('/api/parse-resume', {
          method: 'POST',
          body: formData
        })
        .then(response => {
          if (!response.ok) {
            throw new Error('Authentication or file format error.');
          }
          return response.json();
        })
        .then(data => {
          const rowSuccess = document.createElement('div');
          rowSuccess.className = 'log-row';
          rowSuccess.style.color = 'var(--color-mint)';
          rowSuccess.textContent = `[SUCCESS] MATCH METRICS COMPILED. ATS SCORE: ${data.score}%`;
          terminalLogs.appendChild(rowSuccess);

          setTimeout(() => {
            terminalLogs.classList.remove('active');
            if (holoCard) holoCard.classList.remove('is-scanning');
            
            // Render results
            document.querySelector('.insight-item:nth-child(1) .insight-val').textContent = `${data.score}%`;
            document.querySelector('.insight-item:nth-child(3) .insight-val').textContent = data.missing || 'None';
            document.querySelector('.insight-item:nth-child(4) .insight-val').textContent = data.recommendations || 'None';
            
            revealDashboardMatchScore(data.score);
            
            // Also update the dashboard stats panel if it exists
            const statsResumeScore = document.getElementById('statsResumeScore');
            const statsResumeFill = document.getElementById('statsResumeFill');
            if (statsResumeScore) statsResumeScore.textContent = `${data.score}%`;
            if (statsResumeFill) statsResumeFill.style.width = `${data.score}%`;
            
            // Optional: Insert activity row at the top of recentActivitiesList
            const activitiesList = document.getElementById('recentActivitiesList');
            if (activitiesList) {
              const activeItem = document.createElement('div');
              activeItem.className = 'activity-timeline-row';
              activeItem.innerHTML = `<span class="activity-time">Just now</span><p>Uploaded resume <strong>${file.name}</strong> and ran parsing audits. Scored <strong>${data.score}%</strong>.</p>`;
              activitiesList.insertBefore(activeItem, activitiesList.firstChild);
            }
          }, 800);
        })
        .catch(err => {
          const rowErr = document.createElement('div');
          rowErr.className = 'log-row';
          rowErr.style.color = '#f87171';
          rowErr.textContent = `[ERROR] ${err.message}`;
          terminalLogs.appendChild(rowErr);
          
          setTimeout(() => {
            terminalLogs.classList.remove('active');
            if (holoCard) holoCard.classList.remove('is-scanning');
            uploadZone.style.display = 'flex';
            showToast('ERROR', 'Resume scan aborted: ' + err.message);
          }, 2000);
        });
      }
    }, 400);
  }

  function revealDashboardMatchScore(targetScore) {
    gaugeContainer.classList.add('active');
    
    let currentScore = 0;
    const scoreAnim = setInterval(() => {
      if (currentScore <= targetScore) {
        scoreVal.textContent = currentScore;
        const offset = 471 - (471 * currentScore) / 100;
        if (gaugeCircle) gaugeCircle.style.strokeDashoffset = offset;
        currentScore++;
      } else {
        clearInterval(scoreAnim);
        insightsDashboard.classList.add('active');
        showToast('COMPLETED', 'Resume successfully analyzed and matching metrics compiled.');
      }
    }, 22);
  }

  if (uploadZone) {
    uploadZone.addEventListener('click', (e) => {
      if (e.target.id === 'resumeFileInput') return;
      resumeFileInput.click();
    });
    
    resumeFileInput.addEventListener('change', () => {
      if (resumeFileInput.files.length > 0) {
        uploadAndScanResume(resumeFileInput.files[0]);
      }
    });
    
    uploadZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadZone.style.borderColor = 'var(--color-mint)';
      uploadZone.style.background = 'rgba(0, 255, 204, 0.04)';
    });

    uploadZone.addEventListener('dragleave', () => {
      uploadZone.style.borderColor = 'rgba(255, 255, 255, 0.12)';
      uploadZone.style.background = 'rgba(255, 255, 255, 0.01)';
    });

    uploadZone.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadZone.style.borderColor = 'rgba(255, 255, 255, 0.12)';
      uploadZone.style.background = 'rgba(255, 255, 255, 0.01)';
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        uploadAndScanResume(files[0]);
      }
    });
  }

  if (scanTriggerBtn) {
    scanTriggerBtn.addEventListener('click', () => {
      switchTab('resume');
      setTimeout(() => {
        if (resumeFileInput) resumeFileInput.click();
      }, 400);
    });
  }

  if (downloadReportBtn) {
    downloadReportBtn.addEventListener('click', () => {
      showToast('DOWNLOAD ENGAGED', 'Generating PDF analysis report download stream...');
    });
  }

  // ==========================================
  // --- 8. Dashboard: AI Mock Interview Coach ---
  // ==========================================
  const generateInterviewBtn = document.getElementById('generateInterviewBtn');
  const interviewSetupForm = document.getElementById('interviewSetupForm');
  const activeQuestionBox = document.getElementById('activeQuestionBox');
  const questionText = document.getElementById('questionText');
  const qNum = document.getElementById('qNum');
  const timerVal = document.getElementById('timerVal');
  const answerInput = document.getElementById('answerInput');
  const micSimBtn = document.getElementById('micSimBtn');
  const micText = document.getElementById('micText');
  const submitAnswerBtn = document.getElementById('submitAnswerBtn');
  const interviewResultBox = document.getElementById('interviewResultBox');
  const resultScoreVal = document.getElementById('resultScoreVal');
  const wavesContainer = document.getElementById('wavesContainer');
  const waveBars = document.querySelectorAll('.wave-bar');
  const voiceInstruction = document.getElementById('voiceInstruction');

  const questionsDeck = {
    "Frontend Engineer": [
      "How do you optimize render performance in a high-scale React application?",
      "Explain your strategy for managing state across complex async UI pipelines.",
      "How would you approach configuring a secure, performant micro-frontend layout?"
    ],
    "Lead AI Architect": [
      "How do you optimize model latency constraints when serving public API inferences?",
      "Design a pipeline to handle active vector indexing under massive dataset writes.",
      "What is your architectural strategy to prevent context window retrieval collapse?"
    ],
    "Product Manager": [
      "How do you prioritize architectural tech debt against immediate roadmap deliverables?",
      "Describe how you coordinate alignment metrics across divergent business structures.",
      "How do you evaluate MVP success ratio metrics in pre-product market fit phases?"
    ],
    "Data Scientist": [
      "Describe how you handle covariance shifts and feature leaks inside production models.",
      "Explain the trade-offs between linear transformers and sliding window attention mechanisms.",
      "Design a real-time anomaly parsing model configuration under volatile noise conditions."
    ]
  };

  let selectedRole = "Frontend Engineer";
  let activeQuestionIndex = 0;
  let stopwatchInterval;
  let elapsedSeconds = 0;
  let micActive = false;
  let micModInterval;

  function updateStopwatch() {
    elapsedSeconds++;
    const mins = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
    const secs = (elapsedSeconds % 60).toString().padStart(2, '0');
    timerVal.textContent = `${mins}:${secs}`;
  }

  window.resetInterviewWorkspace = function() {
    // Show setup form
    interviewSetupForm.style.display = 'block';
    activeQuestionBox.style.display = 'none';
    interviewResultBox.style.display = 'none';
    voiceInstruction.textContent = "Voice visualizer standby. Initialize question deck to activate audio simulation.";
  }

  let interviewResponses = [];

  if (generateInterviewBtn) {
    generateInterviewBtn.addEventListener('click', () => {
      selectedRole = document.getElementById('jobRole').value;
      const targetCompany = document.getElementById('targetCompany').value;
      activeQuestionIndex = 0;
      elapsedSeconds = 0;
      interviewResponses = [];
      
      // UI Transitions
      interviewSetupForm.style.display = 'none';
      activeQuestionBox.style.display = 'block';
      
      // Load first question
      qNum.textContent = "1";
      questionText.textContent = "Generating custom questions based on resume and target company...";
      answerInput.value = '';
      timerVal.textContent = '00:00';
      
      // Fetch targeted company-specific questions
      fetch('/api/generate-targeted-interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: selectedRole, company: targetCompany })
      })
      .then(response => response.json())
      .then(data => {
        if (data.questions && data.questions.length > 0) {
          questionsDeck[selectedRole] = data.questions;
          questionText.textContent = questionsDeck[selectedRole][0];
          
          // Start Timer
          clearInterval(stopwatchInterval);
          stopwatchInterval = setInterval(updateStopwatch, 1000);
          
          showToast('SIMULATION LAUNCHED', `AI generated targeted deck for ${selectedRole} at ${targetCompany}.`);
        } else {
          questionText.textContent = questionsDeck[selectedRole][0];
          clearInterval(stopwatchInterval);
          stopwatchInterval = setInterval(updateStopwatch, 1000);
        }
      })
      .catch(error => {
        console.error("Error generating targeted deck:", error);
        questionText.textContent = questionsDeck[selectedRole][0];
        clearInterval(stopwatchInterval);
        stopwatchInterval = setInterval(updateStopwatch, 1000);
      });
    });
  }

  if (micSimBtn) {
    micSimBtn.addEventListener('click', () => {
      micActive = !micActive;
      if (micActive) {
        micSimBtn.style.background = 'var(--color-amethyst)';
        micSimBtn.style.color = '#fff';
        micText.textContent = "Streaming Mic (Active)";
        wavesContainer.classList.add('wave-active');
        voiceInstruction.textContent = "Coach audio streaming active. Speak to record response.";
        
        // Modulate visualizer waves
        micModInterval = setInterval(() => {
          waveBars.forEach(bar => {
            if (Math.random() > 0.4) {
              const height = Math.floor(Math.random() * 32) + 8;
              bar.style.height = `${height}px`;
            }
          });
        }, 100);
      } else {
        clearInterval(micModInterval);
        micSimBtn.style.background = 'rgba(255,255,255,0.03)';
        micSimBtn.style.color = 'var(--text-main)';
        micText.textContent = "Simulate Audio Mic";
        wavesContainer.classList.remove('wave-active');
        voiceInstruction.textContent = "Microphone muted. Voice visualizer standby.";
        waveBars.forEach(bar => bar.style.height = '6px');
      }
    });
  }

  if (submitAnswerBtn) {
    submitAnswerBtn.addEventListener('click', () => {
      const answer = answerInput.value.trim();
      const currentQuestion = questionsDeck[selectedRole][activeQuestionIndex];
      
      if (!answer) {
        showToast('WARNING', 'Please type or speak a response before submitting.');
        return;
      }

      submitAnswerBtn.disabled = true;
      submitAnswerBtn.textContent = "Analyzing Response...";

      fetch('/api/evaluate-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          role: selectedRole,
          question: currentQuestion,
          answer: answer
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Could not evaluate answer. Connection unstable.');
        }
        return response.json();
      })
      .then(data => {
        interviewResponses.push(data);
        
        activeQuestionIndex++;
        submitAnswerBtn.disabled = false;
        submitAnswerBtn.textContent = "Submit Response";

        if (activeQuestionIndex < 3) {
          // Load next question
          qNum.textContent = activeQuestionIndex + 1;
          questionText.textContent = questionsDeck[selectedRole][activeQuestionIndex];
          answerInput.value = '';
          
          // Reset question timer
          elapsedSeconds = 0;
          showToast('PROGRESS', `Question ${activeQuestionIndex} response evaluated. Ingesting next deck node...`);
        } else {
          // End simulation and generate aggregated feedback
          clearInterval(stopwatchInterval);
          activeQuestionBox.style.display = 'none';
          interviewResultBox.style.display = 'block';
          
          // Reset mic if active
          if (micActive) micSimBtn.click();
          
          // Compute cumulative values
          const averageScore = Math.round(
            interviewResponses.reduce((acc, curr) => acc + curr.score, 0) / interviewResponses.length
          );
          
          resultScoreVal.textContent = `${averageScore}%`;
          
          // Render cumulative feedback strengths & corrections
          const strengthsText = interviewResponses.map((r, i) => `Q${i+1}: ${r.strengths}`).join(' ');
          const correctionsText = interviewResponses.map((r, i) => `Q${i+1}: ${r.corrections}`).join(' ');
          
          document.getElementById('resultStrengths').textContent = strengthsText;
          document.getElementById('resultCorrections').textContent = correctionsText;
          
          // Update the dashboard stats panel if it exists
          const statsReadinessScore = document.getElementById('statsReadinessScore');
          const statsReadinessFill = document.getElementById('statsReadinessFill');
          if (statsReadinessScore) statsReadinessScore.textContent = `${averageScore}%`;
          if (statsReadinessFill) statsReadinessFill.style.width = `${averageScore}%`;

          // Add to recent activity log
          const activitiesList = document.getElementById('recentActivitiesList');
          if (activitiesList) {
            const activeItem = document.createElement('div');
            activeItem.className = 'activity-timeline-row';
            activeItem.innerHTML = `<span class="activity-time">Just now</span><p>Completed <strong>${selectedRole}</strong> mock interview session. Average rating: <strong>${averageScore}%</strong>.</p>`;
            activitiesList.insertBefore(activeItem, activitiesList.firstChild);
          }

          showToast('COMPLETED', 'Interview mock review processed successfully.');
        }
      })
      .catch(err => {
        submitAnswerBtn.disabled = false;
        submitAnswerBtn.textContent = "Submit Response";
        showToast('ERROR', err.message);
      });
    });
  }

  // Miscellaneous CTAs
  const forgotPassBtn = document.getElementById('forgotPassBtn');
  if (forgotPassBtn) {
    forgotPassBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('RECOVERY SECURED', 'Email credential recovery token transmission initiated.');
    });
  }

  const bellBtn = document.getElementById('bellBtn');
  if (bellBtn) {
    bellBtn.addEventListener('click', () => {
      showToast('NOTIFICATIONS', 'System update log: All operations synced at nominal state.');
      document.querySelector('.bell-dot').style.display = 'none';
    });
  }

  // --- 9. Landing Page: Newsletter & Contact Submissions ---
  const newsletterForm = document.getElementById('newsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = newsletterForm.querySelector('input[type="email"]');
      const email = emailInput.value.trim();
      const submitBtn = newsletterForm.querySelector('button[type="submit"]');
      
      submitBtn.disabled = true;
      submitBtn.textContent = "Subscribing...";
      
      fetch('/api/subscribe-newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      })
      .then(response => {
        if (!response.ok) throw new Error("Could not process subscription.");
        return response.json();
      })
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Subscribe";
        emailInput.value = '';
        showToast('SUBSCRIBED', data.message);
      })
      .catch(err => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Subscribe";
        showToast('ERROR', err.message);
      });
    });
  }

  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = document.getElementById('contact-name');
      const emailInput = document.getElementById('contact-email');
      const messageInput = document.getElementById('contact-message');
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      
      const name = nameInput.value.trim();
      const email = emailInput.value.trim();
      const message = messageInput.value.trim();
      
      // Frontend Validations
      if (!name) {
        showToast('ERROR', 'Name is required.');
        return;
      }
      if (!email) {
        showToast('ERROR', 'Email is required.');
        return;
      }
      const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
      if (!emailRegex.test(email)) {
        showToast('ERROR', 'Please enter a valid email address.');
        return;
      }
      if (!message) {
        showToast('ERROR', 'Message is required.');
        return;
      }
      if (message.length < 10) {
        showToast('ERROR', 'Message must be at least 10 characters long.');
        return;
      }
      
      // Prevent duplicate submissions & show loading state
      submitBtn.disabled = true;
      submitBtn.textContent = "Sending Message...";
      
      fetch('/api/submit-contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, email: email, message: message })
      })
      .then(response => {
        return response.json().then(data => {
          if (!response.ok) {
            throw new Error(data.error || data.message || "Could not deliver contact payload.");
          }
          return data;
        });
      })
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Send Message";
        nameInput.value = '';
        emailInput.value = '';
        messageInput.value = '';
        showToast('SUCCESS', "Message sent successfully! We'll get back to you soon.");
      })
      .catch(err => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Send Message";
        showToast('ERROR', err.message);
      });
    });
  }

  // --- 10. Social Auth Redirects ---
  const googleLoginBtn = document.getElementById('googleLoginBtn');
  if (googleLoginBtn) {
    googleLoginBtn.addEventListener('click', () => {
      window.location.href = '/google-login';
    });
  }

  const googleSignupBtn = document.getElementById('googleSignupBtn');
  if (googleSignupBtn) {
    googleSignupBtn.addEventListener('click', () => {
      window.location.href = '/google-login';
    });
  }
  // --- 11. Negotiation Coach API integration ---
  const btnGenNegotiation = document.getElementById('btnGenNegotiation');
  if (btnGenNegotiation) {
    btnGenNegotiation.addEventListener('click', () => {
      const companyInput = document.getElementById('neg-company');
      const roleInput = document.getElementById('neg-role');
      const company = companyInput.value.trim();
      const role = roleInput.value.trim();
      
      if (!company) {
        showToast('ERROR', 'Please enter a target company.');
        return;
      }
      if (!role) {
        showToast('ERROR', 'Please enter a target job title.');
        return;
      }
      
      btnGenNegotiation.disabled = true;
      btnGenNegotiation.textContent = "Analyzing Market Data...";
      
      fetch('/api/generate-negotiation-strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: company, role: role })
      })
      .then(response => {
        if (!response.ok) throw new Error("Could not compute negotiation metrics.");
        return response.json();
      })
      .then(data => {
        btnGenNegotiation.disabled = false;
        btnGenNegotiation.textContent = "Analyze Compensation";
        
        document.getElementById('negEmptyBox').style.display = 'none';
        document.getElementById('negResultsBox').style.display = 'flex';
        
        document.getElementById('negLowVal').textContent = data.low;
        document.getElementById('negMedVal').textContent = data.median;
        document.getElementById('negHighVal').textContent = data.high;
        
        document.getElementById('scriptExpectation').textContent = data.expectation_script;
        document.getElementById('scriptCounter').textContent = data.counter_script;
        
        showToast('STRATEGY READY', 'AI compensation playbook generated.');
      })
      .catch(err => {
        btnGenNegotiation.disabled = false;
        btnGenNegotiation.textContent = "Analyze Compensation";
        showToast('ERROR', err.message);
      });
    });
  }
});

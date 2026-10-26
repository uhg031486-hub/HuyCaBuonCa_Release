with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\css\style.css", "a", encoding="utf-8") as f:
    f.write("""

/* Cinematic Mode Entry Button */
.btn-header-cinematic {
  background: linear-gradient(135deg, #E50914 0%, #990000 100%) !important;
  color: #fff !important;
  border: 1px solid #F5C518 !important;
  box-shadow: 0 0 12px rgba(229, 9, 20, 0.45) !important;
  font-weight: 800 !important;
  text-decoration: none !important;
  display: inline-flex !important;
  align-items: center !important;
}
.btn-header-cinematic:hover {
  transform: scale(1.05) !important;
  box-shadow: 0 0 18px rgba(245, 197, 24, 0.6) !important;
}
""")
print("Appended CSS successfully!")

import time
import sys

LOG_FILE = "data/access.log"

def add_log(line):
    """Add a log line to the file"""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
        print(f"✅ Added: {line[:80]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_sql_injection():
    print("\n🔴 Testing SQL Injection...")
    add_log('192.168.1.100 - - [29/Jan/2026 10:00:00] "GET /api?id=1\' OR \'1\'=\'1 HTTP/1.1" 200 512')
    time.sleep(1)

def test_xss():
    print("\n🔴 Testing XSS Attack...")
    add_log('192.168.1.101 - - [29/Jan/2026 10:01:00] "GET /search?q=<script>alert(\'XSS\')</script> HTTP/1.1" 200 256')
    time.sleep(1)

def test_path_traversal():
    print("\n🔴 Testing Path Traversal...")
    add_log('192.168.1.102 - - [29/Jan/2026 10:02:00] "GET /files/../../etc/passwd HTTP/1.1" 200 128')
    time.sleep(1)

def test_command_injection():
    print("\n🔴 Testing Command Injection...")
    add_log('192.168.1.103 - - [29/Jan/2026 10:03:00] "GET /exec?cmd=; cat /etc/passwd HTTP/1.1" 200 512')
    time.sleep(1)

def test_brute_force():
    print("\n🔴 Testing Brute Force (6 requests from same IP)...")
    for i in range(6):
        add_log(f'192.168.1.104 - - [29/Jan/2026 10:04:0{i}] "GET /admin HTTP/1.1" 401 512')
        time.sleep(0.5)

def test_correlated_attacks():
    print("\n🔴 Testing Correlated Attacks (same IP, multiple attack types)...")
    add_log('192.168.1.105 - - [29/Jan/2026 10:05:00] "GET /api?id=1\' UNION SELECT * FROM users-- HTTP/1.1" 200 512')
    time.sleep(1)
    add_log('192.168.1.105 - - [29/Jan/2026 10:05:01] "GET /search?q=<img src=x onerror=alert(1)> HTTP/1.1" 200 256')
    time.sleep(1)
    add_log('192.168.1.105 - - [29/Jan/2026 10:05:02] "GET /api/../../config.php HTTP/1.1" 200 128')
    time.sleep(1)

def main():
    print("=" * 60)
    print("🛡️  SENTINEL ATTACK TEST SUITE")
    print("=" * 60)
    
    try:
        test_sql_injection()
        test_xss()
        test_path_traversal()
        test_command_injection()
        test_brute_force()
        test_correlated_attacks()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)
        print("\n📊 Check your Sentinel window for alerts!")
        print("🔗 Refresh dashboard at http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

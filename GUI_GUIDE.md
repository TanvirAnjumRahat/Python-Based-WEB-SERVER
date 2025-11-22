# PyNetLite GUI Quick Start Guide

## 🚀 Launching the GUI

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Launch the Application
```powershell
python run_gui.py
```

## 📖 Using the Control Panel

### Configuration Panel ⚙️

The top section allows you to configure your server:

1. **Host**: Server IP address (default: 127.0.0.1)
   - `127.0.0.1` - Local machine only
   - `0.0.0.0` - All network interfaces

2. **Port**: Server port number (default: 8080)
   - Choose any available port (1024-65535 recommended)
   - GUI will warn if port is already in use

3. **Root Directory**: Location of static files
   - Click "Browse..." to select folder
   - Default: `public/`

4. **Enable File Caching**: Toggle caching on/off
   - Improves performance for repeated requests
   - Uses LRU (Least Recently Used) algorithm

### Control Buttons 🎛️

- **▶ Start Server**: Launch the web server
  - Validates configuration
  - Checks port availability
  - Starts server in background thread

- **⬛ Stop Server**: Gracefully stop the server
  - Disabled when server is not running

- **🗑️ Clear Logs**: Clear the log display
  - Useful for decluttering
  - Doesn't affect server operation

- **🌐 Open Browser**: Launch default browser
  - Opens server URL automatically
  - Only enabled when server is running

### Status Panel 📊

Real-time server information:

- **Status**: Visual indicator (● Running / ● Stopped)
- **URL**: Click-ready server address
- **Uptime**: Automatic time tracking (HH:MM:SS format)

### Log Viewer 📋

Color-coded log messages:

- 🔵 **INFO** (Blue): General information
- ✅ **SUCCESS** (Green): Successful operations
- 🟡 **WARN** (Yellow): Warnings
- 🔴 **ERROR** (Red): Errors
- 🟣 **DEBUG** (Purple): Debug information

## 💡 Tips & Best Practices

### Testing Your Server

1. Start the server using GUI
2. Click "Open Browser" or manually visit the URL
3. Check logs for incoming requests
4. Test different endpoints:
   - `/` - Homepage
   - `/api/time` - Current server time
   - `/api/echo?msg=hello` - Echo service

### Troubleshooting

**Problem**: "Port already in use" error
- **Solution**: Change port number or stop conflicting application

**Problem**: "Address already in use" error on 0.0.0.0
- **Solution**: Another service is using that port, try different port

**Problem**: Server not responding
- **Solution**: Check firewall settings, verify host/port in browser URL

**Problem**: Static files not found
- **Solution**: Verify root directory path, check file permissions

### Development Workflow

1. Configure server settings
2. Place HTML/CSS/JS files in root directory
3. Start server
4. Edit files (server auto-serves updated content)
5. Refresh browser to see changes
6. Monitor logs for errors

### Production Deployment

⚠️ **Note**: This server is educational. For production:
- Consider using production WSGI servers (gunicorn, uWSGI)
- Implement proper security measures
- Add HTTPS support
- Use reverse proxy (nginx, Apache)

## 🎨 GUI Features Showcase

### Modern Design
- Clean, professional interface
- Color-coded status indicators
- Intuitive layout following UX best practices
- Responsive to user actions

### Real-time Feedback
- Instant status updates
- Live log streaming
- Uptime counter
- Visual button states

### Error Handling
- Port conflict detection
- Configuration validation
- Graceful shutdown prompts
- User-friendly error messages

## ⌨️ Keyboard Shortcuts

- **Ctrl+Q**: Quit application
- **F1**: Help (opens this guide)
- **F5**: Refresh configuration
- **Ctrl+L**: Clear logs

## 🔧 Advanced Configuration

### Custom Root Directory Structure
```
your-root/
├── index.html          # Homepage
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── api/
    └── data.json
```

### Multiple Instances
Run multiple servers on different ports:
1. Launch first GUI instance (e.g., port 8080)
2. Launch second GUI instance (e.g., port 8081)
3. Each runs independently

### Log Management
- Logs show in real-time
- Scroll to view history
- Clear periodically for performance
- Copy/paste for debugging

## 📚 Additional Resources

- Main README: `README.md`
- Technical Report: `REPORT.md`
- Source Code: `src/webserver/`
- Tests: `tests/`

## 🆘 Getting Help

If you encounter issues:
1. Check logs for error messages
2. Verify configuration settings
3. Review this guide
4. Check GitHub issues
5. Contact maintainer

---

**Enjoy your PyNetLite server! 🌐✨**

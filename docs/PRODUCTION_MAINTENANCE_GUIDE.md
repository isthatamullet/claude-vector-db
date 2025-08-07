# Production Maintenance Guide

## Overview
This guide covers the maintenance procedures for the production Claude Code Vector Database System.

## Regular Maintenance Schedule

### Weekly Maintenance (Automated)
```bash
bash maintenance/weekly_production_maintenance.sh
```
- System health checks
- Performance monitoring  
- Database status review
- Backup verification

### Monthly Optimization
```bash
bash maintenance/monthly_optimization.sh  
```
- Extended performance analysis
- Archive cleanup review
- Log file management
- System statistics

### Critical Issue Monitoring
```bash
bash system/production_alerts.sh
```
- MCP server health
- Database accessibility
- Hook integration status
- Disk space monitoring

## Performance Monitoring

### Performance Targets
- **Search Response**: <500ms
- **Database Init**: <2000ms  
- **Memory Usage**: <200MB
- **System Reliability**: 99%+ uptime

### Performance Testing
```bash
bash system/performance_monitor.sh
```

## Maintenance Logs
- Weekly maintenance logs: Check output of maintenance scripts
- Performance trends: Monitor query response times
- System growth: Track database size and entry count

## Emergency Procedures
1. **System Unresponsive**: Run production_alerts.sh for diagnosis
2. **Performance Degradation**: Run performance_monitor.sh for analysis  
3. **Database Issues**: Check ChromaDB integrity and disk space
4. **MCP Problems**: Verify MCP server can start and restart Claude Code

## Archive Management
- **Migration Backup**: Review quarterly for cleanup (currently preserved)
- **Log Files**: Archive logs >30 days old monthly
- **Temporary Files**: Clean .tmp and .log files during maintenance

## Production Status
System is fully operational with zero functionality loss from refactoring.
All original capabilities preserved with enhanced organization and performance.
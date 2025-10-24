import React from 'react';
import { motion } from 'framer-motion';
import { Search, Download, Upload, RefreshCw, FileText, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { formatRelativeTime } from '../../utils/formatters';
import { cn } from '../../lib/utils';

const ActivityFeed = ({ activities }) => {
  const getActivityIcon = (type) => {
    const icons = {
      analysis: Search,
      collection: Download,
      upload: Upload,
      soup: RefreshCw
    };
    return icons[type] || FileText;
  };

  const getStatusIcon = (status) => {
    const icons = {
      success: CheckCircle,
      error: XCircle,
      warning: AlertCircle,
      info: Info
    };
    return icons[status] || Info;
  };

  const getStatusColor = (status) => {
    const colors = {
      success: 'text-command-green',
      error: 'text-threat-red',
      warning: 'text-hazard-yellow',
      info: 'text-soft-cyan'
    };
    return colors[status] || 'text-muted-foreground';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activities.map((activity, index) => {
            const ActivityIcon = getActivityIcon(activity.type);
            const StatusIcon = getStatusIcon(activity.status);
            
            return (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="p-2 rounded-md bg-primary/10">
                  <ActivityIcon className="w-4 h-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground">{activity.message}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatRelativeTime(activity.timestamp)}
                  </p>
                </div>
                <StatusIcon className={cn('w-4 h-4 flex-shrink-0', getStatusColor(activity.status))} />
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default ActivityFeed;
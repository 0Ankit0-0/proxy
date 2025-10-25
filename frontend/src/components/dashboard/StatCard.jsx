import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';
import { formatNumber } from '../../utils/formatters';

const StatCard = ({ title, value, subtitle, icon: Icon, trend, className }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <Card className={cn('overflow-hidden', className)}>
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <div className="flex items-baseline gap-2">
                <h3 className="text-3xl font-bold text-foreground">
                  {formatNumber(value)}
                </h3>
                {subtitle && (
                  <span className="text-sm text-muted-foreground">{subtitle}</span>
                )}
              </div>
              {trend && (
                <p className={cn(
                  'text-xs font-medium',
                  trend > 0 ? 'text-command-green' : 'text-threat-red'
                )}>
                  {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
                </p>
              )}
            </div>
            {Icon && (
              <div className="p-3 rounded-lg bg-primary/10">
                <Icon className="w-6 h-6 text-primary" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default StatCard;
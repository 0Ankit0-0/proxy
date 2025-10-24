import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Clock, Server, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { formatTimestamp, formatScore, formatDetectionType } from '../../utils/formatters';
import { cn } from '../../lib/utils';

const ThreatCard = ({ threat }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant={threat.severity}>
                {threat.severity.toUpperCase()}
              </Badge>
              <Badge variant="outline">
                {formatDetectionType(threat.detection_type)}
              </Badge>
              <span className="text-sm text-muted-foreground">
                Score: <span className="font-mono font-semibold">{formatScore(threat.score)}</span>
              </span>
            </div>
            <AlertTriangle className={cn(
              'w-5 h-5 flex-shrink-0',
              threat.severity === 'critical' && 'text-severity-critical',
              threat.severity === 'high' && 'text-severity-high',
              threat.severity === 'medium' && 'text-severity-medium',
              threat.severity === 'low' && 'text-severity-low'
            )} />
          </div>

          {/* Body */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              <span>{formatTimestamp(threat.timestamp)}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Server className="w-4 h-4" />
              <span className="font-mono">{threat.host}</span>
            </div>
            <p className="text-foreground mt-2">{threat.message}</p>
          </div>

          {/* Expand Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
            className="w-full"
          >
            {expanded ? (
              <>
                Show Less <ChevronUp className="w-4 h-4 ml-2" />
              </>
            ) : (
              <>
                Show Details <ChevronDown className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>

          {/* Expanded Details */}
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="pt-4 border-t border-border">
                  <h4 className="text-sm font-semibold text-foreground mb-3">Additional Details</h4>
                  <pre className="text-xs bg-secondary p-4 rounded-md overflow-x-auto text-muted-foreground font-mono">
                    {JSON.stringify(threat.details, null, 2)}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
};

export default ThreatCard;
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

const ThreatChart = ({ data }) => {
  const COLORS = {
    critical: '#FF3B3B',
    high: '#FF8C42',
    medium: '#FFC300',
    low: '#7FD3F5'
  };

  const chartData = [
    { name: 'Critical', value: data.critical, color: COLORS.critical },
    { name: 'High', value: data.high, color: COLORS.high },
    { name: 'Medium', value: data.medium, color: COLORS.medium },
    { name: 'Low', value: data.low, color: COLORS.low }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Threat Severity Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{
              background: '#0F1417',
              border: '1px solid rgba(148, 163, 184, 0.2)',
              borderRadius: '8px',
              color: '#E6EEF3'
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default ThreatChart;
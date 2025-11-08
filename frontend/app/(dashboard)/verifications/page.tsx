"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Download, Eye, ArrowUpDown, Calendar } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { RiskBadge, getRiskLevel, type RiskLevel } from '@/src/components/dashboard/RiskBadge';
import { Input } from '@/src/components/ui/input';
import { Button } from '@/src/components/ui/button';
import { Badge } from '@/src/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/src/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/src/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/card';
import { staggerChildren, fadeIn } from '@/lib/animations';

// Mock data - will be replaced with Supabase queries
const mockVerifications = [
  {
    id: '1',
    candidateName: 'Sarah Johnson',
    position: 'Senior Software Engineer',
    company: 'Tech Corp',
    riskScore: 15,
    status: 'completed',
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    flags: 0,
  },
  {
    id: '2',
    candidateName: 'Michael Chen',
    position: 'Product Manager',
    company: 'StartupXYZ',
    riskScore: 65,
    status: 'flagged',
    timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    flags: 3,
  },
  {
    id: '3',
    candidateName: 'Emily Rodriguez',
    position: 'UX Designer',
    company: 'Design Studio',
    riskScore: 8,
    status: 'completed',
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    flags: 0,
  },
  {
    id: '4',
    candidateName: 'James Wilson',
    position: 'Data Scientist',
    company: 'AI Labs',
    riskScore: 42,
    status: 'processing',
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    flags: 1,
  },
  {
    id: '5',
    candidateName: 'Lisa Anderson',
    position: 'Marketing Director',
    company: 'Marketing Inc',
    riskScore: 12,
    status: 'completed',
    timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    flags: 0,
  },
  {
    id: '6',
    candidateName: 'David Kim',
    position: 'DevOps Engineer',
    company: 'Cloud Systems',
    riskScore: 78,
    status: 'flagged',
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    flags: 4,
  },
  {
    id: '7',
    candidateName: 'Maria Garcia',
    position: 'Frontend Developer',
    company: 'Web Agency',
    riskScore: 18,
    status: 'completed',
    timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    flags: 0,
  },
  {
    id: '8',
    candidateName: 'Robert Taylor',
    position: 'Backend Engineer',
    company: 'API Solutions',
    riskScore: 35,
    status: 'completed',
    timestamp: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
    flags: 1,
  },
];

type SortField = 'name' | 'date' | 'risk';
type SortDirection = 'asc' | 'desc';
type StatusFilter = 'all' | 'completed' | 'processing' | 'flagged';
type RiskFilter = 'all' | RiskLevel;

export default function VerificationsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [riskFilter, setRiskFilter] = useState<RiskFilter>('all');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Filter and sort logic
  const filteredVerifications = mockVerifications
    .filter((v) => {
      const matchesSearch = 
        v.candidateName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        v.position.toLowerCase().includes(searchQuery.toLowerCase()) ||
        v.company.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || v.status === statusFilter;
      
      const riskLevel = getRiskLevel(v.riskScore);
      const matchesRisk = riskFilter === 'all' || riskLevel === riskFilter;
      
      return matchesSearch && matchesStatus && matchesRisk;
    })
    .sort((a, b) => {
      let comparison = 0;
      
      switch (sortField) {
        case 'name':
          comparison = a.candidateName.localeCompare(b.candidateName);
          break;
        case 'date':
          comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          break;
        case 'risk':
          comparison = a.riskScore - b.riskScore;
          break;
      }
      
      return sortDirection === 'asc' ? comparison : -comparison;
    });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerChildren}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={fadeIn}>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Verifications</h1>
        <p className="text-[#9ca3af]">
          Browse and manage all candidate verification reports
        </p>
      </motion.div>

      {/* Filters Card */}
      <motion.div variants={fadeIn}>
        <Card className="glass border-white/10">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#6b7280]" />
                <Input
                  type="text"
                  placeholder="Search by name, position, or company..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-white/5 border-white/10 focus:border-purple-500/50"
                />
              </div>

              {/* Status Filter */}
              <Select value={statusFilter} onValueChange={(v: string) => setStatusFilter(v as StatusFilter)}>
                <SelectTrigger className="w-full lg:w-[180px] bg-white/5 border-white/10">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="flagged">Flagged</SelectItem>
                </SelectContent>
              </Select>

              {/* Risk Filter */}
              <Select value={riskFilter} onValueChange={(v: string) => setRiskFilter(v as RiskFilter)}>
                <SelectTrigger className="w-full lg:w-[180px] bg-white/5 border-white/10">
                  <SelectValue placeholder="Risk Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Risks</SelectItem>
                  <SelectItem value="low">Low Risk</SelectItem>
                  <SelectItem value="medium">Medium Risk</SelectItem>
                  <SelectItem value="high">High Risk</SelectItem>
                  <SelectItem value="critical">Critical Risk</SelectItem>
                </SelectContent>
              </Select>

              {/* Export Button */}
              <Button
                variant="outline"
                className="border-white/10 hover:bg-white/5"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Results Count */}
      <motion.div variants={fadeIn} className="text-sm text-[#9ca3af]">
        Showing {filteredVerifications.length} of {mockVerifications.length} verifications
      </motion.div>

      {/* Table Card */}
      <motion.div variants={fadeIn}>
        <Card className="glass border-white/10">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-white/10 hover:bg-transparent">
                    <TableHead 
                      className="cursor-pointer select-none"
                      onClick={() => toggleSort('name')}
                    >
                      <div className="flex items-center gap-2">
                        Candidate
                        <ArrowUpDown className="w-4 h-4" />
                      </div>
                    </TableHead>
                    <TableHead>Position</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead 
                      className="cursor-pointer select-none"
                      onClick={() => toggleSort('risk')}
                    >
                      <div className="flex items-center gap-2">
                        Risk Level
                        <ArrowUpDown className="w-4 h-4" />
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer select-none"
                      onClick={() => toggleSort('date')}
                    >
                      <div className="flex items-center gap-2">
                        Date
                        <ArrowUpDown className="w-4 h-4" />
                      </div>
                    </TableHead>
                    <TableHead className="text-center">Flags</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredVerifications.map((verification) => {
                    const riskLevel = getRiskLevel(verification.riskScore);
                    
                    return (
                      <TableRow 
                        key={verification.id}
                        className="border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
                        onClick={() => router.push(`/dashboard/report/${verification.id}`)}
                      >
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div
                              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                                verification.status === 'completed'
                                  ? 'bg-green-400'
                                  : verification.status === 'flagged'
                                  ? 'bg-red-400'
                                  : 'bg-yellow-400 animate-pulse'
                              }`}
                            />
                            <div>
                              <div className="font-medium text-white">
                                {verification.candidateName}
                              </div>
                              <div className="text-sm text-[#6b7280]">
                                {verification.company}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-[#9ca3af]">
                          {verification.position}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={`${
                              verification.status === 'completed'
                                ? 'bg-green-500/10 text-green-400 border-green-500/30'
                                : verification.status === 'flagged'
                                ? 'bg-red-500/10 text-red-400 border-red-500/30'
                                : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                            }`}
                          >
                            {verification.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <RiskBadge level={riskLevel} score={verification.riskScore} />
                        </TableCell>
                        <TableCell className="text-[#9ca3af]">
                          {new Date(verification.timestamp).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                          })}
                        </TableCell>
                        <TableCell className="text-center">
                          {verification.flags > 0 ? (
                            <Badge
                              variant="outline"
                              className="bg-orange-500/10 text-orange-400 border-orange-500/30"
                            >
                              {verification.flags}
                            </Badge>
                          ) : (
                            <span className="text-[#6b7280]">—</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e: React.MouseEvent) => {
                              e.stopPropagation();
                              router.push(`/dashboard/report/${verification.id}`);
                            }}
                            className="hover:bg-white/10"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}

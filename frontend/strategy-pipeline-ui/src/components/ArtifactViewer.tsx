import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  FileJson
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ArtifactViewerProps {
  artifact: unknown;
  artifactType: string;
  title?: string;
}

export function ArtifactViewer({ artifact, artifactType, title }: ArtifactViewerProps) {
  const [copied, setCopied] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['main']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };


  if (!artifact || typeof artifact !== 'object') {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-muted-foreground">No artifact data available</p>
        </CardContent>
      </Card>
    );
  }

  const data = artifact as Record<string, unknown>;

  return (
    <div className="space-y-4">
      {/* Header with copy button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">{title || artifactType}</h3>
          <p className="text-sm text-muted-foreground">
            {Object.keys(data).length} fields
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => copyToClipboard(JSON.stringify(data, null, 2))}
          >
            {copied ? (
              <>
                <Check className="mr-2 h-4 w-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="mr-2 h-4 w-4" />
                Copy JSON
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Artifact content */}
      <Card>
        <CardContent className="p-6 space-y-4">
          {Object.entries(data).map(([key, value]) => {
            if (key === 'id' || key === 'created_at' || key === 'updated_at' || key === 'status') {
              return null; // Skip metadata fields
            }

            const isExpanded = expandedSections.has(key);
            const isComplex = typeof value === 'object' && value !== null;

            return (
              <div key={key} className="space-y-2">
                <div
                  className={cn(
                    "flex items-center gap-2",
                    isComplex && "cursor-pointer hover:bg-accent/50 rounded p-2"
                  )}
                  onClick={() => isComplex && toggleSection(key)}
                >
                  {isComplex && (
                    isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    )
                  )}
                  <h4 className="font-medium capitalize">
                    {key.replace(/_/g, ' ')}
                  </h4>
                  {Array.isArray(value) && (
                    <Badge variant="secondary" className="ml-2">
                      {value.length} items
                    </Badge>
                  )}
                </div>

                {isExpanded && (
                  <div className="pl-6 space-y-2">
                    {Array.isArray(value) ? (
                      <ul className="list-disc list-inside space-y-1">
                        {value.map((item, idx) => (
                          <li key={idx} className="text-sm">
                            {typeof item === 'object' ? (
                              <pre className="mt-1 p-2 bg-muted rounded text-xs overflow-x-auto">
                                {JSON.stringify(item, null, 2)}
                              </pre>
                            ) : (
                              <span>{String(item)}</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    ) : typeof value === 'object' && value !== null ? (
                      <pre className="p-3 bg-muted rounded text-xs overflow-x-auto">
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        {String(value)}
                      </p>
                    )}
                  </div>
                )}

                <Separator className="mt-2" />
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Raw JSON view (collapsible) */}
      <div className="space-y-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => toggleSection('raw')}
          className="w-full justify-start"
        >
          {expandedSections.has('raw') ? (
            <ChevronDown className="mr-2 h-4 w-4" />
          ) : (
            <ChevronRight className="mr-2 h-4 w-4" />
          )}
          <FileJson className="mr-2 h-4 w-4" />
          View Raw JSON
        </Button>

        {expandedSections.has('raw') && (
          <Card>
            <CardContent className="p-4">
              <pre className="text-xs overflow-x-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

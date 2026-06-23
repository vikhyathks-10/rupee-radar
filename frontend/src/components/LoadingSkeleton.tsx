
export function SkeletonPulse({ className }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-200 rounded ${className || ''}`} />
}

export function DashboardSkeleton() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* 4 Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="p-5 border rounded-xl bg-white space-y-3">
            <SkeletonPulse className="w-10 h-10 rounded-lg" />
            <SkeletonPulse className="h-4 w-24" />
            <SkeletonPulse className="h-6 w-32" />
          </div>
        ))}
      </div>

      {/* 2 charts / lists */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="border rounded-xl bg-white p-6 space-y-4">
          <SkeletonPulse className="h-6 w-48" />
          <SkeletonPulse className="h-[250px] w-full" />
        </div>
        <div className="border rounded-xl bg-white p-6 space-y-4">
          <SkeletonPulse className="h-6 w-48" />
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex justify-between items-center py-2">
                <div className="space-y-2">
                  <SkeletonPulse className="h-4 w-32" />
                  <SkeletonPulse className="h-3 w-40" />
                </div>
                <SkeletonPulse className="h-5 w-20" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Table skeleton */}
      <div className="border rounded-xl bg-white p-6 space-y-4">
        <SkeletonPulse className="h-6 w-48" />
        <div className="space-y-3">
          <div className="flex space-x-4 border-b pb-2">
            {[...Array(5)].map((_, i) => (
              <SkeletonPulse key={i} className="h-4 flex-1" />
            ))}
          </div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex space-x-4 py-2">
              {[...Array(5)].map((_, j) => (
                <SkeletonPulse key={j} className="h-4 flex-1" />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function InsightsSkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
      <div className="space-y-2">
        <SkeletonPulse className="h-8 w-48" />
        <SkeletonPulse className="h-4 w-72" />
      </div>
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="p-5 border rounded-xl bg-white flex gap-4">
            <SkeletonPulse className="w-10 h-10 rounded-lg shrink-0" />
            <div className="flex-1 space-y-3">
              <div className="flex gap-2">
                <SkeletonPulse className="h-5 w-40" />
                <SkeletonPulse className="h-5 w-16 rounded-full" />
              </div>
              <SkeletonPulse className="h-4 w-full" />
              <SkeletonPulse className="h-4 w-5/6" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function ReportSkeleton() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* Page header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <SkeletonPulse className="h-8 w-32" />
          <SkeletonPulse className="h-4 w-72" />
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Preview panel (2/3) */}
        <div className="lg:col-span-2 bg-white border rounded-xl shadow-lg p-8 space-y-8">
          {/* Document header */}
          <div className="border-b pb-6 flex justify-between items-end">
            <div className="space-y-2">
              <SkeletonPulse className="h-8 w-40" />
              <SkeletonPulse className="h-4 w-56" />
            </div>
            <div className="space-y-1.5 text-right">
              <SkeletonPulse className="h-3 w-48" />
              <SkeletonPulse className="h-3 w-36" />
            </div>
          </div>

          {/* Section 1 — metrics grid */}
          <div className="space-y-3">
            <SkeletonPulse className="h-6 w-40" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="p-4 bg-gray-50 rounded-lg border space-y-2">
                  <SkeletonPulse className="h-3 w-20" />
                  <SkeletonPulse className="h-6 w-24" />
                </div>
              ))}
            </div>
          </div>

          {/* Section 2 — category table */}
          <div className="space-y-3">
            <SkeletonPulse className="h-6 w-48" />
            <div className="border rounded-lg overflow-hidden">
              <div className="bg-gray-50 flex space-x-4 px-4 py-3 border-b">
                {[...Array(4)].map((_, i) => (
                  <SkeletonPulse key={i} className="h-3 flex-1" />
                ))}
              </div>
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex space-x-4 px-4 py-3 border-b last:border-0">
                  {[...Array(4)].map((_, j) => (
                    <SkeletonPulse key={j} className="h-4 flex-1" />
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Section 3 — insights */}
          <div className="space-y-3">
            <SkeletonPulse className="h-6 w-52" />
            {[...Array(2)].map((_, i) => (
              <div key={i} className="p-4 border rounded-lg space-y-2">
                <SkeletonPulse className="h-4 w-48" />
                <SkeletonPulse className="h-3 w-full" />
                <SkeletonPulse className="h-3 w-5/6" />
              </div>
            ))}
          </div>
        </div>

        {/* Side panel (1/3) */}
        <div className="lg:col-span-1 bg-white border rounded-xl shadow-sm p-6 space-y-6">
          <SkeletonPulse className="w-12 h-12 rounded-full mx-auto" />
          <div className="space-y-2 text-center">
            <SkeletonPulse className="h-6 w-40 mx-auto" />
            <SkeletonPulse className="h-4 w-56 mx-auto" />
          </div>
          <SkeletonPulse className="h-12 w-full rounded-xl" />
          <SkeletonPulse className="h-10 w-full rounded-xl" />
        </div>
      </div>
    </div>
  )
}

export default function DashboardLoading() {
  return (
    <main className="min-h-screen bg-[#f5f7f9] px-4 py-6 text-[#162033] sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
          <div className="h-4 w-40 rounded bg-slate-200" />
          <div className="mt-4 h-8 w-72 max-w-full rounded bg-slate-200" />
          <div className="mt-3 h-4 w-56 rounded bg-slate-100" />
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {["one", "two", "three", "four"].map((item) => (
            <div
              key={item}
              className="min-h-32 rounded-md border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div className="h-4 w-24 rounded bg-slate-200" />
              <div className="mt-6 h-8 w-16 rounded bg-slate-200" />
              <div className="mt-4 h-4 w-36 rounded bg-slate-100" />
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

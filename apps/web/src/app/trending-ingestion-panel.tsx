"use client";

import { CheckCircle2, LoaderCircle, RefreshCw, TriangleAlert } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export type TrendingRun = {
  id: number;
  period: string;
  language: string | null;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
};

type TrendingIngestionPanelProps = {
  initialRun: TrendingRun | null;
  period: string;
  language: string;
};

const periodLabels: Record<string, string> = {
  daily: "日榜",
  weekly: "周榜",
  monthly: "月榜",
};

function formatFinishedAt(value: string | null): string {
  if (!value) {
    return "尚未抓取";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
}

export function TrendingIngestionPanel({
  initialRun,
  period,
  language,
}: TrendingIngestionPanelProps) {
  const router = useRouter();
  const [run, setRun] = useState(initialRun);
  const [state, setState] = useState<"idle" | "running" | "success" | "error">("idle");
  const [error, setError] = useState("");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (state !== "running") {
      return;
    }
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [state]);

  async function startIngestion() {
    setState("running");
    setError("");
    setElapsedSeconds(0);

    const params = new URLSearchParams({ period });
    if (language) {
      params.set("language", language);
    }

    try {
      const response = await fetch(`/api/ingest/trending?${params.toString()}`, { method: "POST" });
      const body = (await response.json()) as TrendingRun | { detail?: string };
      if (!response.ok) {
        throw new Error("detail" in body && body.detail ? body.detail : `抓取失败（${response.status}）`);
      }
      setRun(body as TrendingRun);
      setState("success");
      router.refresh();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "抓取失败");
      setState("error");
    }
  }

  const isRunning = state === "running";
  const statusText =
    state === "success"
      ? "抓取完成"
      : state === "error"
        ? "抓取失败"
        : run?.status === "success"
          ? "数据已同步"
          : run?.status === "failed"
            ? "上次抓取失败"
            : "等待首次抓取";

  return (
    <section className="flex flex-col gap-4 border-y border-[#244169] py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          {isRunning ? (
            <LoaderCircle className="animate-spin text-cyan" size={18} aria-hidden="true" />
          ) : state === "error" || run?.status === "failed" ? (
            <TriangleAlert className="text-amber" size={18} aria-hidden="true" />
          ) : (
            <CheckCircle2 className="text-emerald-400" size={18} aria-hidden="true" />
          )}
          <h2 className="text-sm font-black text-ink">GitHub 数据同步</h2>
          <span className="font-mono text-xs font-bold text-cyan">{statusText}</span>
        </div>
        <p className="mt-1.5 text-xs font-semibold text-muted">
          {isRunning
            ? `正在抓取 ${periodLabels[period] ?? period}${language ? ` · ${language}` : ""}，已用时 ${elapsedSeconds}s`
            : error || `最近完成：${formatFinishedAt(run?.finished_at ?? null)}`}
        </p>
        {isRunning ? (
          <div className="mt-3 h-1.5 w-full max-w-sm overflow-hidden rounded-full bg-[#20395d]">
            <span className="block h-full w-2/3 animate-pulse rounded-full bg-cyan" />
          </div>
        ) : null}
      </div>
      <button
        type="button"
        onClick={startIngestion}
        disabled={isRunning}
        className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 text-sm font-black text-white transition hover:bg-orange-400 disabled:cursor-wait disabled:bg-[#28415f] disabled:text-muted"
      >
        <RefreshCw className={isRunning ? "animate-spin" : ""} size={16} aria-hidden="true" />
        {isRunning ? "抓取中" : "立即抓取"}
      </button>
    </section>
  );
}

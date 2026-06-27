import { NextRequest, NextResponse } from "next/server";
import { ingestionLimitForPeriod } from "../../../trending-ingestion-config";

const apiBaseUrl = process.env.REPO_SCOUT_API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const params = new URLSearchParams();
  const period = request.nextUrl.searchParams.get("period") ?? "daily";
  params.set("period", period);
  params.set("limit", String(ingestionLimitForPeriod(period)));

  const language = request.nextUrl.searchParams.get("language");
  if (language) {
    params.set("language", language);
  }

  try {
    const response = await fetch(`${apiBaseUrl}/api/admin/ingest/trending?${params.toString()}`, {
      method: "POST",
      cache: "no-store",
      signal: AbortSignal.timeout(35_000),
    });
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "GitHub Trending 抓取服务不可用" }, { status: 502 });
  }
}

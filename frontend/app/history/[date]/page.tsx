import { HistoryDetailClient } from "./detail-client";

export default async function HistoryDetailPage(props: PageProps<"/history/[date]">) {
  const { date } = await props.params;
  return <HistoryDetailClient date={date} />;
}

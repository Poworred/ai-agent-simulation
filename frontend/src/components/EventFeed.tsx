import { formatSimTime } from "@/lib/time";
import type { Event } from "@/types/simulation";

type Props = {
  events: Event[];
};

export function EventFeed({ events }: Props) {
  return (
    <aside className="panel eventFeed">
      <h2>事件流</h2>
      {events.length === 0 ? <p className="emptyHint">事件会在这里成为可回放记忆。</p> : null}
      {events.map((event) => (
        <article key={event.id} className="eventItem">
          <span className={`tag tag-${event.event_type}`}>{event.event_type}</span>
          <time>{formatSimTime(event.day, event.minute)}</time>
          <p>{event.summary}</p>
          {event.details ? <small>{event.details}</small> : null}
        </article>
      ))}
    </aside>
  );
}

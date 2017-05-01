SELECT
  c.date,
  t.trip_id,
  st.stop_sequence,
  t.route_id,
  t.service_id,
  t.trip_short_name,
  r.route_short_name,
  r.route_long_name,
  r.route_type,
  s.stop_name,
  s.stop_lat,
  s.stop_lon,
  LPAD(FLOOR(EXTRACT(EPOCH FROM st.arrival_time) / 3600) :: TEXT, 2, '0') || ':' ||
  LPAD(FLOOR(EXTRACT(EPOCH FROM st.arrival_time) :: INT % 3600 / 60) :: TEXT, 2, '0')   AS arrival_time,
  LPAD(FLOOR(EXTRACT(EPOCH FROM st.departure_time) / 3600) :: TEXT, 2, '0') || ':' ||
  LPAD(FLOOR(EXTRACT(EPOCH FROM st.departure_time) :: INT % 3600 / 60) :: TEXT, 2, '0') AS departure_time,
  u.arrival_delay                                                                       AS arrival_delay_with_nulls,
  u.departure_delay                                                                     AS departure_delay_with_nulls,
  coalesce(u.arrival_delay, 0)                                                          AS arrival_delay,
  coalesce(u.departure_delay, 0)                                                        AS departue_delay
FROM trips t
  INNER JOIN stop_times st ON t.trip_id = st.trip_id
  INNER JOIN stops s ON s.stop_id = st.stop_id
  INNER JOIN routes r ON r.route_id = t.route_id
  INNER JOIN calendar_dates c ON c.service_id = t.service_id
  LEFT JOIN realtime_updates u
    ON t.trip_id = u.trip_id AND s.stop_id = u.stop_id AND c.date = u.trip_start_datetime :: DATE
WHERE  c.date > DATE '2017-04-27' AND c.date < DATE '2017-05-01'
ORDER BY c.date, t.trip_id, st.stop_sequence
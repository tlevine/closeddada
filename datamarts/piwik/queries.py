VISIT = '''
SELECT
  idvisit,
  idsite,
  idvisitor,
  visit_total_actions,
  location_ip,
  location_country,
  location_region,
  location_city,
  location_latitude,
  location_longitude
FROM piwik_log_visit
WHERE idvisit > '%d'
ORDER BY idvisit ASC;
'''

LINK_VISIT_ACTION = '''
SELECT
  idvisit,
  idvisitor,
  idaction_url
FROM piwik_log_link_visit_action
OFFSET %d;
'''

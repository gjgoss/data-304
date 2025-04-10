library()

df <- read.csv('Downloads/daily-new-confirmed-covid-19-cases-per-million-people.csv')


df %>%
  filter(Entity %in% c("United States", "Canada", "Brazil")) %>%
  filter(Day >= as.Date("2021-01-01") & Day <= as.Date("2021-03-01")) %>% 
  group_by(Entity, Day) %>%
  summarize(new_cases = sum(new_cases, na.rm = TRUE)) %>%
  ggplot(aes(x = Day, y = new_cases, group = Entity, color = Entity)) +
  geom_line() +
  labs(title = "Daily New COVID-19 Cases")




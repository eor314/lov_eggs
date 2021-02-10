import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'D:\LOV\Copepod_Functional_Traits_Benedettietal_2015_JPR.csv')
df['avg_len'] = df[['Minimal length [A1]', 'Maximal length [A1]']].values.mean(axis=1)


calanoid_sac = df[(df['Order'] == 'Calanoida') & (df['Spawning strategy'] == 'Sac-spawner')]
print(f"mean min calanoida: {calanoid_sac['Minimal length [A1]'].mean()}")
print(f"mean max calanoida: {calanoid_sac['Maximal length [A1]'].mean()}")

cyclopoid_sac = df[(df['Order'] == 'Cyclopoida') & (df['Spawning strategy'] == 'Sac-spawner')]
print(f"mean min cyclopoida: {cyclopoid_sac['Minimal length [A1]'].mean()}")
print(f"mean max cyclopoida: {cyclopoid_sac['Maximal length [A1]'].mean()}")

fig, ax = plt.subplots()
df['avg_len'].transform('log').hist(bins=10, color='b', alpha=0.6, ax=ax)
df[df['Spawning strategy'] == 'Sac-spawner']['avg_len'].transform('log').hist(bins=10, color='m', alpha=0.6, ax=ax)
ax.grid(False)
ax.set_ylabel('counts')
ax.set_xlabel('log(mm)')
ax.legend(['all copepods', 'egg bearing'])
ax.set_title('Avg cope lengths split by spawning strat from Benedetti etal2015')
#cyclopoid_sac['avg_len'].transform('log').hist(bins=10, color='m', alpha=0.4, ax=ax)
#calanoid_sac['avg_len'].transform('log').hist(bins=10, color='g', alpha=0.4, ax=ax)
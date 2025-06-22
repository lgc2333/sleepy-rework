import { ScrollView, View } from 'react-native'
import { Appbar, Banner, Card, Icon, Text } from 'react-native-paper'

export const title = '欢迎'

export default function Home() {
  return (
    <>
      <Appbar.Header elevated>
        <Appbar.Content title={title} />
      </Appbar.Header>
      <View>
        <Banner visible contentStyle={{ marginTop: -8 }}>
          欢迎使用 Sleepy Rework Android Client！{'\n'}
          如果您是第一次使用，请先前往设置页。
        </Banner>
        <View style={{ padding: 16, gap: 16 }}>
          <Card mode="contained">
            <Card.Title
              style={{ paddingVertical: 20 }}
              title="工作中"
              titleVariant="titleMedium"
              subtitle="已于 xx 时连接到服务器"
              left={(props) => (
                <View style={{ ...props, alignItems: 'center' }}>
                  <Icon source="check-circle" size={32} />
                </View>
              )}
            />
          </Card>
          <Card mode="contained">
            <Card.Title
              style={{ paddingVertical: 20 }}
              title={<Text variant="titleMedium">警告</Text>}
              titleVariant="titleMedium"
              subtitle="未获取到无障碍权限，无法获取到前台应用信息"
              subtitleNumberOfLines={2}
              left={(props) => (
                <View style={{ ...props, alignItems: 'center' }}>
                  <Icon source="alert-circle" size={32} />
                </View>
              )}
            />
          </Card>
          <Card mode="outlined">
            <Card.Content style={{ gap: 8 }}>
              <Text variant="titleSmall">客户端侧当前信息</Text>
              <ScrollView horizontal>
                <Text style={{ fontFamily: 'monospace' }}>
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. {'\n'}
                  Nobis quisquam similique veritatis a ratione inventore dicta magnam
                  eum deleniti, tenetur dolorum, hic ipsa asperiores! {'\n'}
                  Doloremque sunt minima fuga laboriosam. Corrupti.
                </Text>
              </ScrollView>
            </Card.Content>
          </Card>
          <Card mode="outlined">
            <Card.Content style={{ gap: 8 }}>
              <Text variant="titleSmall">服务端侧当前信息</Text>
              <ScrollView horizontal>
                <Text style={{ fontFamily: 'monospace' }}>
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. {'\n'}
                  Nobis quisquam similique veritatis a ratione inventore dicta magnam
                  eum deleniti, tenetur dolorum, hic ipsa asperiores! {'\n'}
                  Doloremque sunt minima fuga laboriosam. Corrupti.
                </Text>
              </ScrollView>
            </Card.Content>
          </Card>
        </View>
      </View>
    </>
  )
}

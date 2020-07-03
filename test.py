def get_table_name(self, exchange=None):
        # switch to a database
        # self.client.switch_database(db_name)
        measurements = self.client.get_list_measurements()
        if exchange is not None:
            table_names = []
            for i in measurements:
                table_names.append(i['name'])
            # in list format
            table_name_exchange = list(sorted([i for i in table_names if exchange in i]))
            return (table_name_exchange)
        else:
            return (measurements)

if __name__ == '__main__':
    print(get_table_name(self))
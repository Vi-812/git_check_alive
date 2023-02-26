# - Для оформления сценария "как запустить на другом ПК" рекомендую попробовать Makefile или Taskfile
# - Рекомендую попробовать Docker для запуска проектов, чтобы не засорять локальный ПК модулями
#
# await g_cli.get_new_report(args.repository_path)
# if __name__ == "__main__":
#     load_dotenv()
#
#     token = os.getenv("APP_TOKEN")
#
#     g_cli = ga.GithubApiClient(token)
#
#     loop = asyncio.get_event_loop()
#
#     loop.run_until_complete(main())
#
#
# [aliases]
# release = sdist bdist_wheel
#
# [bdist_wheel]
# universal = 0
#
# [flake8]
# exclude = .svn,CVS,.bzr,.hg,.git,__pycache,.ropeproject
# max-line-length = 120
# import-order-style = pep8
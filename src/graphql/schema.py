from ariadne import gql

type_defs = gql("""
    directive @requiresAuth on FIELD_DEFINITION
    directive @requiresRole(role: UserRole!) on FIELD_DEFINITION
    
    type Query {
        users(first: Int, after: String, last: Int, before: String): UserConnection! @requiresAuth
        user(id: ID!): User @requiresAuth
        organizations(first: Int, after: String, last: Int, before: String): OrganizationConnection! @requiresAuth
        organization(id: ID!): Organization @requiresAuth
        studies(first: Int, after: String, last: Int, before: String, filter: StudyFilterInput): StudyConnection! @requiresAuth
        study(id: ID!): Study @requiresAuth
        reports(first: Int, after: String, last: Int, before: String, filter: ReportFilterInput): ReportConnection! @requiresAuth
        report(id: ID!): Report @requiresAuth
    }

    type Mutation {
        login(email: String!, password: String!): AuthPayload!
        changePassword(currentPassword: String!, newPassword: String!): Boolean! @requiresAuth
        createUser(input: CreateUserInput!): User! @requiresAuth
        updateUser(id: ID!, input: UpdateUserInput!): User! @requiresAuth
        deleteUser(id: ID!): Boolean! @requiresAuth
        createOrganization(input: CreateOrganizationInput!): Organization! @requiresAuth
        updateOrganization(id: ID!, input: UpdateOrganizationInput!): Organization! @requiresAuth
        deleteOrganization(id: ID!): Boolean! @requiresRole(role: Owner)
        inviteRadiologist(organizationId: ID!, input: InviteRadiologistInput!): User! @requiresRole(role: Owner)
        removeRadiologist(userId: ID!, organizationId: ID!): Boolean! @requiresRole(role: Owner)
        getRadiologistPassword(userId: ID!): String @requiresRole(role: Owner)
        forcePasswordReset(userId: ID!): String! @requiresRole(role: Owner)
        createStudy(input: CreateStudyInput!): Study! @requiresAuth
        updateStudy(id: ID!, input: UpdateStudyInput!): Study! @requiresAuth
        deleteStudy(id: ID!): Boolean! @requiresAuth
        createReport(input: CreateReportInput!): Report! @requiresAuth
        updateReport(id: ID!, input: UpdateReportInput!): Report! @requiresAuth
        deleteReport(id: ID!): Boolean! @requiresAuth
    }

    enum UserRole {
        Owner
        Radiologist
    }

    type AuthPayload {
        token: String!
        user: User!
        mustChangePassword: Boolean!
    }

    type User {
        id: ID!
        firstName: String!
        lastName: String!
        email: String!
        phoneNumber: String
        createdAt: String!
        mustChangePassword: Boolean!
        organizationMemberships: [OrganizationMember!]!
        reports: [Report!]!
    }

    type Organization {
        id: ID!
        name: String!
        logo: String
        address: String!
        phoneNumber: String!
        createdBy: User!
        members: [OrganizationMember!]!
    }

    type OrganizationMember {
        id: ID!
        user: User!
        organization: Organization!
        role: UserRole!
        createdAt: String!
    }

    type Study {
        id: ID!
        name: String!
        categories: [String!]!
        createdAt: String!
        templates: [StudyTemplate!]!
        reports: [Report!]!
    }

    type StudyTemplate {
        id: ID!
        sectionNames: [String!]!
        createdAt: String!
        study: Study!
    }

    type Report {
        id: ID!
        promptText: String
        resultText: String
        status: ReportStatus!
        createdAt: String!
        updatedAt: String
        study: Study!
        template: StudyTemplate
        user: User!
        history: [ReportHistory!]!
        events: [ReportEvent!]!
    }

    type ReportHistory {
        id: ID!
        timestamp: String!
        status: ReportStatus!
        resultText: String
        report: Report!
    }

    type ReportEvent {
        id: ID!
        eventType: String!
        timestamp: String!
        details: String
        report: Report!
    }

    enum ReportStatus {
        DRAFT
        PRELIMINARY
        SIGNED
        SIGNED_WITH_ADDENDUM
    }

    input CreateUserInput {
        firstName: String!
        lastName: String!
        email: String!
        phoneNumber: String
        password: String!
    }

    input UpdateUserInput {
        firstName: String
        lastName: String
        email: String
        phoneNumber: String
    }

    input InviteRadiologistInput {
        firstName: String!
        lastName: String!
        email: String!
        phoneNumber: String
    }

    input CreateOrganizationInput {
        name: String!
        logo: String
        address: String!
        phoneNumber: String!
    }

    input UpdateOrganizationInput {
        name: String
        logo: String
        address: String
        phoneNumber: String
    }

    input CreateStudyInput {
        name: String!
        categories: [String!]
    }

    input UpdateStudyInput {
        name: String
        categories: [String!]
    }

    input CreateReportInput {
        studyId: ID!
        templateId: ID!
        promptText: String!
    }

    input UpdateReportInput {
        promptText: String
        resultText: String
        status: ReportStatus
    }

    type PageInfo {
        hasNextPage: Boolean!
        hasPreviousPage: Boolean!
        startCursor: String
        endCursor: String
    }

    type UserEdge {
        cursor: String!
        node: User!
    }

    type UserConnection {
        edges: [UserEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type OrganizationEdge {
        cursor: String!
        node: Organization!
    }

    type OrganizationConnection {
        edges: [OrganizationEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type OrganizationMemberEdge {
        cursor: String!
        node: OrganizationMember!
    }

    type OrganizationMemberConnection {
        edges: [OrganizationMemberEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type StudyEdge {
        cursor: String!
        node: Study!
    }

    type StudyConnection {
        edges: [StudyEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type ReportEdge {
        cursor: String!
        node: Report!
    }

    type ReportConnection {
        edges: [ReportEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type StudyTemplateEdge {
        cursor: String!
        node: StudyTemplate!
    }

    type StudyTemplateConnection {
        edges: [StudyTemplateEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type ReportHistoryEdge {
        cursor: String!
        node: ReportHistory!
    }

    type ReportHistoryConnection {
        edges: [ReportHistoryEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    type ReportEventEdge {
        cursor: String!
        node: ReportEvent!
    }

    type ReportEventConnection {
        edges: [ReportEventEdge!]!
        pageInfo: PageInfo!
        totalCount: Int!
    }

    input StudyFilterInput {
        categories: [String!]
    }

    input ReportFilterInput {
        studyId: ID
        templateId: ID
        studyCategories: [String!]
    }
""")
